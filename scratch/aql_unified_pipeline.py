# -*- coding: utf-8 -*-
"""
scratch/aql_unified_pipeline.py
---------------------------------
Unified synchronous closed-loop quant pipeline runner.
Acts strictly as an execution coordinator. 
No python-based alpha generation or mutation is contained here.
It polls Render status, archives results to alpha_maker/, and stands by
waiting for Antigravity (the LLM) to write the new generation_N_alphas.json file.
Once detected, it injects them directly into the active simulation queue.
"""

import os
import sys
import json
import time
import requests
import re
from datetime import datetime

# Setup project root path for access
AQL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, AQL_ROOT)

# Render Configs
RENDER_URL = "https://world-quant.onrender.com"
API_TOKEN = "yashthakreop"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Local state paths
SCRATCH_DIR = os.path.dirname(os.path.abspath(__file__))
RUN_LOG_PATH = os.path.join(SCRATCH_DIR, "aql_run_log.txt")

def log_msg(msg, level="INFO"):
    timestamp = datetime.now().isoformat()
    line = f"{timestamp} | [PIPELINE] [{level}] {msg}\n"
    with open(RUN_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())

def main():
    log_msg("======================================================================")
    log_msg("AQL SYNCHRONOUS RUNNER PIPELINE INITIALIZED")
    log_msg("======================================================================")
    
    alpha_maker_dir = os.path.join(AQL_ROOT, "alpha_maker")
    os.makedirs(alpha_maker_dir, exist_ok=True)
    
    # Auto-detect next expected generation number
    generation = 1
    try:
        files = os.listdir(alpha_maker_dir)
        gen_numbers = []
        for f in files:
            m = re.match(r"generation_(\d+)_alphas\.json", f)
            if m:
                gen_numbers.append(int(m.group(1)))
        if gen_numbers:
            generation = max(gen_numbers) + 1
    except Exception as e:
        log_msg(f"Could not auto-detect generation: {e}", "WARNING")
        
    log_msg(f"Active Generation State Tracker: Next expected is Generation {generation}")
    
    # State tracking: "POLLING_SIMULATION" or "AWAITING_LLM"
    # Auto-transition to AWAITING_LLM if the expected generation file is already present on disk
    target_file = os.path.join(alpha_maker_dir, f"generation_{generation}_alphas.json")
    if os.path.exists(target_file):
        current_state = "AWAITING_LLM"
        log_msg(f"Detected target file on startup. Starting in AWAITING_LLM state for Generation {generation}")
    else:
        current_state = "POLLING_SIMULATION"
        
    last_processed_count = -1
    
    while True:
        try:
            if current_state == "POLLING_SIMULATION":
                # 1. Query Render queue status
                url = f"{RENDER_URL}/api/queue-status"
                r = requests.get(url, headers=HEADERS, timeout=30)
                if r.status_code != 200:
                    log_msg(f"Failed to query queue status: HTTP {r.status_code}", "WARNING")
                    time.sleep(300)
                    continue
                    
                status_data = r.json()
                in_disk = status_data.get("queue_on_disk", 0)
                in_mem = status_data.get("in_memory", 0)
                pipeline_status = status_data.get("pipeline_status", "UNKNOWN")
                
                log_msg(f"Queue Status: Disk={in_disk} | In-Mem={in_mem} | State={pipeline_status}")
                
                # Check if queue has completed simulation
                if (in_disk == 0 and in_mem == 0) or pipeline_status == "COMPLETED":
                    log_msg("Cloud backtest queue has finished simulation. Querying vault statistics...")
                    
                    stats_url = f"{RENDER_URL}/api/stats"
                    sr = requests.get(stats_url, headers=HEADERS, timeout=30)
                    if sr.status_code == 200:
                        stats = sr.json()
                        vault_alphas = stats.get("vault_alphas", [])
                        
                        # Archive results if new ones found
                        if len(vault_alphas) > 0 and len(vault_alphas) != last_processed_count:
                            last_processed_count = len(vault_alphas)
                            
                            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                            report_path = os.path.join(alpha_maker_dir, f"simulation_results_{timestamp_str}.json")
                            with open(report_path, "w", encoding="utf-8") as rf:
                                json.dump({
                                    "timestamp": datetime.now().isoformat(),
                                    "total_simulated": len(vault_alphas),
                                    "vault_alphas": vault_alphas
                                }, rf, indent=2)
                            log_msg(f"[ARCHIVED] simulation_results_{timestamp_str}.json written successfully.")
                            
                        log_msg(f"[STANDBY] Vault results archived. Awaiting Antigravity (LLM) to write 'generation_{generation}_alphas.json'...")
                        current_state = "AWAITING_LLM"
                    else:
                        log_msg(f"Failed to query stats: HTTP {sr.status_code}", "WARNING")
                        
            elif current_state == "AWAITING_LLM":
                # Check if the LLM has generated and written the next generation file
                target_file = os.path.join(alpha_maker_dir, f"generation_{generation}_alphas.json")
                if os.path.exists(target_file):
                    log_msg(f"[DETECTED] New evolved file found: generation_{generation}_alphas.json! Parsing payload...")
                    
                    try:
                        with open(target_file, "r", encoding="utf-8") as f:
                            payload = json.load(f)
                            # Support both {"mutated_alphas": [...]} wrapper or direct list
                            alphas_list = payload.get("mutated_alphas", payload) if isinstance(payload, dict) else payload
                            
                        if not isinstance(alphas_list, list) or len(alphas_list) == 0:
                            log_msg("Invalid or empty alphas list in JSON.", "WARNING")
                            time.sleep(300)
                            continue
                            
                        log_msg(f"Loaded {len(alphas_list)} formulas from LLM payload. Injecting directly into active simulation queue...")
                        
                        # Push directly to Render active simulation queue
                        overwrite_url = f"{RENDER_URL}/api/overwrite-queue"
                        ores = requests.post(overwrite_url, headers=HEADERS, json=alphas_list, timeout=30)
                        
                        if ores.status_code == 200 and ores.json().get("status") == "ok":
                            added_count = ores.json().get("overwritten_count", 0)
                            log_msg(f"[SUCCESS] Remote simulation queue overwritten directly: added {added_count} active backtests.")
                            
                            # Resume simulation pipeline execution
                            requests.post(f"{RENDER_URL}/api/start-pipeline", headers=HEADERS, timeout=30)
                            
                            # Increment generation, reset state to polling
                            generation += 1
                            current_state = "POLLING_SIMULATION"
                        else:
                            log_msg(f"[WARNING] Remote direct queue overwrite failed: {ores.text}", "WARNING")
                    except Exception as e:
                        log_msg(f"Failed to process LLM file: {e}", "WARNING")
                else:
                    # Silent waiting prints in console
                    print(f"[{time.strftime('%H:%M:%S')}] [STANDBY] Waiting for Antigravity to write 'alpha_maker/generation_{generation}_alphas.json'...")
                    
        except Exception as e:
            log_msg(f"Pipeline loop warning: {e}", "WARNING")
            
        time.sleep(300) # Poll/Wait every 5 minutes

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
scratch/split_slot_orchestrator.py
-----------------------------------
Orchestrates split slot executions for Yash Thakre OPI (slots 1-4) 
and Yash Thakre OPI Pro (slots 5-8) independently.
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

from src.config import OPI_API_TOKEN, OPI_PRO_API_TOKEN

RENDER_URL = "https://world-quant.onrender.com"

# Setup profile specific tokens and endpoints
OPI_HEADERS = {
    "Authorization": f"Bearer {OPI_API_TOKEN}",
    "Content-Type": "application/json"
}

OPI_PRO_HEADERS = {
    "Authorization": f"Bearer {OPI_PRO_API_TOKEN}",
    "Content-Type": "application/json"
}

# Local state paths
SCRATCH_DIR = os.path.dirname(os.path.abspath(__file__))
OPI_LOG_PATH = os.path.join(SCRATCH_DIR, "opi_run_log.txt")
OPI_PRO_LOG_PATH = os.path.join(SCRATCH_DIR, "opipro_run_log.txt")

def log_msg(msg, is_pro=False):
    timestamp = datetime.now().isoformat()
    prefix = "[OPI-PRO]" if is_pro else "[OPI]"
    line = f"{timestamp} | {prefix} {msg}\n"
    log_path = OPI_PRO_LOG_PATH if is_pro else OPI_LOG_PATH
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())

def run_opi_task():
    log_msg("OPI pipeline executor initialized (Slots 1-4)")
    alpha_maker_dir = os.path.join(AQL_ROOT, "alpha_maker")
    
    # Auto detect generation
    generation = 1
    try:
        files = os.listdir(alpha_maker_dir)
        gen_numbers = [int(m.group(1)) for f in files if (m := re.match(r"opi_generation_(\d+)_alphas\.json", f))]
        if gen_numbers:
            generation = max(gen_numbers) + 1
    except Exception as e:
        log_msg(f"Error checking OPI generation: {e}")

    log_msg(f"Next expected generation: OPI Generation {generation}")
    
    # Simple polling loop
    while True:
        try:
            # Query server queue status specifically for slots 1-4
            url = f"{RENDER_URL}/api/queue-status"
            r = requests.get(url, headers=OPI_HEADERS, timeout=30)
            if r.status_code == 200:
                status_data = r.json()
                in_disk = status_data.get("queue_on_disk", 0)
                in_mem = status_data.get("in_memory", 0)
                pipeline_status = status_data.get("pipeline_status", "UNKNOWN")
                
                log_msg(f"Queue status: Disk={in_disk} | In-Mem={in_mem} | State={pipeline_status}")
                
                if (in_disk == 0 and in_mem == 0) or pipeline_status == "COMPLETED":
                    log_msg("OPI slots 1-4 finished simulation. Querying results...")
                    
                    stats_url = f"{RENDER_URL}/api/stats"
                    sr = requests.get(stats_url, headers=OPI_HEADERS, timeout=30)
                    if sr.status_code == 200:
                        vault_alphas = sr.json().get("vault_alphas", [])
                        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                        report_path = os.path.join(alpha_maker_dir, f"opi_results_{timestamp_str}.json")
                        with open(report_path, "w", encoding="utf-8") as rf:
                            json.dump({
                                "timestamp": datetime.now().isoformat(),
                                "total_simulated": len(vault_alphas),
                                "vault_alphas": vault_alphas
                            }, rf, indent=2)
                        log_msg(f"[ARCHIVED] opi_results_{timestamp_str}.json written successfully.")
                        log_msg(f"Awaiting Antigravity to write 'opi_generation_{generation}_alphas.json'...")
                        
                        # Wait for next generation file
                        target_file = os.path.join(alpha_maker_dir, f"opi_generation_{generation}_alphas.json")
                        while not os.path.exists(target_file):
                            time.sleep(60)
                        
                        # Load and push
                        with open(target_file, "r", encoding="utf-8") as f:
                            payload = json.load(f)
                        
                        log_msg(f"Found {len(payload)} formulas. Overwriting queue on slots 1-4...")
                        overwrite_url = f"{RENDER_URL}/api/overwrite-queue"
                        ores = requests.post(overwrite_url, headers=OPI_HEADERS, json=payload, timeout=30)
                        if ores.status_code == 200:
                            log_msg("[SUCCESS] Slots 1-4 updated successfully. Resuming pipeline...")
                            requests.post(f"{RENDER_URL}/api/start-pipeline", headers=OPI_HEADERS, timeout=30)
                            generation += 1
            else:
                log_msg(f"Queue API warning: HTTP {r.status_code}")
        except Exception as e:
            log_msg(f"OPI pipeline exception: {e}")
        time.sleep(300)

def run_opipro_task():
    log_msg("OPI-PRO pipeline executor initialized (Slots 5-8)", is_pro=True)
    alpha_maker_dir = os.path.join(AQL_ROOT, "alpha_maker")
    
    # Auto detect generation
    generation = 1
    try:
        files = os.listdir(alpha_maker_dir)
        gen_numbers = [int(m.group(1)) for f in files if (m := re.match(r"opipro_generation_(\d+)_alphas\.json", f))]
        if gen_numbers:
            generation = max(gen_numbers) + 1
    except Exception as e:
        log_msg(f"Error checking OPI-PRO generation: {e}", is_pro=True)

    log_msg(f"Next expected generation: OPI-PRO Generation {generation}", is_pro=True)
    
    # Simple polling loop
    while True:
        try:
            # Query server queue status specifically for slots 5-8
            # In a split deployment, OPI Pro uses world-quant-1.onrender.com or distinct query headers
            url = "https://world-quant-1.onrender.com/api/queue-status"
            r = requests.get(url, headers=OPI_PRO_HEADERS, timeout=30)
            if r.status_code == 200:
                status_data = r.json()
                in_disk = status_data.get("queue_on_disk", 0)
                in_mem = status_data.get("in_memory", 0)
                pipeline_status = status_data.get("pipeline_status", "UNKNOWN")
                
                log_msg(f"Queue status: Disk={in_disk} | In-Mem={in_mem} | State={pipeline_status}", is_pro=True)
                
                if (in_disk == 0 and in_mem == 0) or pipeline_status == "COMPLETED":
                    log_msg("OPI-PRO slots 5-8 finished simulation. Querying results...", is_pro=True)
                    
                    stats_url = "https://world-quant-1.onrender.com/api/stats"
                    sr = requests.get(stats_url, headers=OPI_PRO_HEADERS, timeout=30)
                    if sr.status_code == 200:
                        vault_alphas = sr.json().get("vault_alphas", [])
                        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                        report_path = os.path.join(alpha_maker_dir, f"opipro_results_{timestamp_str}.json")
                        with open(report_path, "w", encoding="utf-8") as rf:
                            json.dump({
                                "timestamp": datetime.now().isoformat(),
                                "total_simulated": len(vault_alphas),
                                "vault_alphas": vault_alphas
                            }, rf, indent=2)
                        log_msg(f"[ARCHIVED] opipro_results_{timestamp_str}.json written successfully.", is_pro=True)
                        log_msg(f"Awaiting Antigravity to write 'opipro_generation_{generation}_alphas.json'...", is_pro=True)
                        
                        # Wait for next generation file
                        target_file = os.path.join(alpha_maker_dir, f"opipro_generation_{generation}_alphas.json")
                        while not os.path.exists(target_file):
                            time.sleep(60)
                        
                        # Load and push
                        with open(target_file, "r", encoding="utf-8") as f:
                            payload = json.load(f)
                        
                        log_msg(f"Found {len(payload)} formulas. Overwriting queue on slots 5-8...", is_pro=True)
                        overwrite_url = "https://world-quant-1.onrender.com/api/overwrite-queue"
                        ores = requests.post(overwrite_url, headers=OPI_PRO_HEADERS, json=payload, timeout=30)
                        if ores.status_code == 200:
                            log_msg("[SUCCESS] Slots 5-8 updated successfully. Resuming pipeline...", is_pro=True)
                            requests.post("https://world-quant-1.onrender.com/api/start-pipeline", headers=OPI_PRO_HEADERS, timeout=30)
                            generation += 1
            else:
                log_msg(f"Queue API warning: HTTP {r.status_code}", is_pro=True)
        except Exception as e:
            log_msg(f"OPI-PRO pipeline exception: {e}", is_pro=True)
        time.sleep(300)

if __name__ == "__main__":
    import threading
    t1 = threading.Thread(target=run_opi_task)
    t2 = threading.Thread(target=run_opipro_task)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()

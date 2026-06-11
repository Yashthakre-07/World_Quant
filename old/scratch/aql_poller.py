# -*- coding: utf-8 -*-
"""
scratch/aql_poller.py
-----------------------
Background telemetry daemon that polls Render simulation stats,
determines batch completion, and serializes feedback for mutation.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

# Render Server Configurations
RENDER_URL = "https://world-quant.onrender.com"
BEARER_TOKEN = "yashthakreop"
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# Local state paths
SCRATCH_DIR = os.path.dirname(os.path.abspath(__file__))
FEEDBACK_FILE = os.path.join(SCRATCH_DIR, "aql_feedback.json")
RUN_LOG_PATH = os.path.join(SCRATCH_DIR, "aql_run_log.txt")

def log_msg(msg, level="INFO"):
    timestamp = datetime.now().isoformat()
    line = f"{timestamp} | [POLLER] [{level}] {msg}\n"
    with open(RUN_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())

def poll_render_status():
    """Queries the Render status API."""
    try:
        url = f"{RENDER_URL}/api/queue-status"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            return r.json()
        else:
            log_msg(f"Failed to query queue status: HTTP {r.status_code}", "WARNING")
            return None
    except Exception as e:
        log_msg(f"Error querying queue status: {e}", "WARNING")
        return None

def fetch_vault_stats():
    """Queries the complete vault statistics including all alpha runs."""
    try:
        url = f"{RENDER_URL}/api/stats"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            return r.json()
        else:
            log_msg(f"Failed to fetch stats: HTTP {r.status_code}", "WARNING")
            return None
    except Exception as e:
        log_msg(f"Error fetching stats: {e}", "WARNING")
        return None

def main():
    log_msg("======================================================================")
    log_msg("AQL TELEMETRY POLLER DAEMON INITIALIZED")
    log_msg("======================================================================")
    
    last_processed_count = -1
    
    while True:
        # 1. Check queue status on the server
        status_data = poll_render_status()
        if not status_data:
            time.sleep(30)
            continue
            
        in_disk = status_data.get("queue_on_disk", 0)
        in_mem = status_data.get("in_memory", 0)
        pipeline_status = status_data.get("pipeline_status", "UNKNOWN")
        
        log_msg(f"Queue Status: Disk={in_disk} | In-Mem={in_mem} | State={pipeline_status}")
        
        # 2. If the queue is fully cleared on the server, a batch has completed!
        if in_disk == 0 and in_mem == 0:
            log_msg("Cloud queue is empty. Fetching completed simulation vault stats...")
            
            stats = fetch_vault_stats()
            if stats:
                vault_alphas = stats.get("vault_alphas", [])
                log_msg(f"Total simulated alphas in vault: {len(vault_alphas)}")
                
                # If we have newly completed alphas, serialize feedback for re-engineering
                if len(vault_alphas) > 0 and len(vault_alphas) != last_processed_count:
                    last_processed_count = len(vault_alphas)
                    
                    # Capture candidates needing optimization (SOFT_FAIL, HARD_REJECT, ERROR)
                    pending_feedback = []
                    for val in vault_alphas:
                        status = val.get("status", "PENDING")
                        if status in ("SOFT_FAIL", "HARD_REJECT", "ERROR"):
                            pending_feedback.append(val)
                            
                    # Save a copy of the vault results report in the alpha_maker folder
                    report_dir = os.path.join(os.path.dirname(SCRATCH_DIR), "alpha_maker")
                    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                    report_path = os.path.join(report_dir, f"simulation_results_{timestamp_str}.json")
                    
                    try:
                        os.makedirs(report_dir, exist_ok=True)
                        with open(report_path, "w", encoding="utf-8") as rf:
                            json.dump({
                                "timestamp": datetime.now().isoformat(),
                                "total_simulated": len(vault_alphas),
                                "vault_alphas": vault_alphas
                            }, rf, indent=2)
                        log_msg(f"Simulation results archived successfully to: alpha_maker/simulation_results_{timestamp_str}.json")
                    except Exception as e:
                        log_msg(f"Failed to archive results to alpha_maker folder: {e}", "WARNING")
                        
                    feedback_payload = {
                        "timestamp": datetime.now().isoformat(),
                        "total_simulated": len(vault_alphas),
                        "pending_optimization_count": len(pending_feedback),
                        "alphas": pending_feedback[:30] # Keep payload compact
                    }
                    
                    # Save feedback file locally for Antigravity or Orchestrator
                    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
                        json.dump(feedback_payload, f, indent=2)
                        
                    log_msg(f"Dumped {len(pending_feedback)} failed runs to {FEEDBACK_FILE} for mutation analysis.")
            
        # Poll every 300 seconds (5 minutes) to minimize network traffic
        time.sleep(300)

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
scratch/run_dual_pipeline.py
----------------------------
Executes separate scheduling and evolution tasks for:
- Group A: Slots 1-4 (Token: yashthakreop)
- Group B: Slots 5-8 (Token: yashthakrepro)

They run concurrently in separate background threads, sharing the same prompt logic.
"""

import os
import sys
import json
import time
import requests
import re
import threading
from datetime import datetime

# Setup project root path for access
AQL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, AQL_ROOT)

from src.config import GROUPA_API_TOKEN, GROUPB_API_TOKEN

RENDER_URL = "https://world-quant.onrender.com"

# Setup headers
GROUPA_HEADERS = {
    "Authorization": f"Bearer {GROUPA_API_TOKEN}",
    "Content-Type": "application/json"
}

GROUPB_HEADERS = {
    "Authorization": f"Bearer {GROUPB_API_TOKEN}",
    "Content-Type": "application/json"
}

# Logs
SCRATCH_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRATCH_DIR, "dual_pipeline_run_log.txt")

def log_msg(group, msg):
    timestamp = datetime.now().isoformat()
    line = f"{timestamp} | [{group}] {msg}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())

def group_a_loop():
    log_msg("GroupA", "Executor thread started (Slots 1-4)")
    alpha_maker_dir = os.path.join(AQL_ROOT, "alpha_maker")
    
    # Detect expected generation
    generation = 1
    try:
        files = os.listdir(alpha_maker_dir)
        gen_numbers = [int(m.group(1)) for f in files if (m := re.match(r"groupa_generation_(\d+)_alphas\.json", f))]
        if gen_numbers:
            generation = max(gen_numbers) + 1
    except Exception as e:
        log_msg("GroupA", f"Error checking generations: {e}")
        
    log_msg("GroupA", f"Next expected file: groupa_generation_{generation}_alphas.json")

    while True:
        try:
            # Query queue status from render server 1 (OPI slots 1-4)
            r = requests.get(f"{RENDER_URL}/api/queue-status", headers=GROUPA_HEADERS, timeout=30)
            if r.status_code == 200:
                data = r.json()
                
                # Check for Group A pause/stop flags (if the endpoint returns active status)
                # If pipeline_status is PAUSED or custom endpoint check returns groupa_active = False, sleep and bypass
                if data.get("pipeline_status") == "PAUSED":
                    log_msg("GroupA", "Group A execution is paused by operator. Standing by...")
                    time.sleep(30)
                    continue
                
                in_disk = data.get("queue_on_disk", 0)
                in_mem = data.get("in_memory", 0)
                pipeline_status = data.get("pipeline_status", "UNKNOWN")
                
                log_msg("GroupA", f"Queue status: Disk={in_disk} | In-Mem={in_mem} | State={pipeline_status}")
                
                if (in_disk == 0 and in_mem == 0) or pipeline_status == "COMPLETED":
                    log_msg("GroupA", "Slots 1-4 finished simulation. Querying statistics...")
                    
                    sr = requests.get(f"{RENDER_URL}/api/stats", headers=GROUPA_HEADERS, timeout=30)
                    if sr.status_code == 200:
                        vault_alphas = sr.json().get("vault_alphas", [])
                        
                        # Archive stats
                        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                        report_path = os.path.join(alpha_maker_dir, f"groupa_results_{timestamp_str}.json")
                        with open(report_path, "w", encoding="utf-8") as rf:
                            json.dump({
                                "timestamp": datetime.now().isoformat(),
                                "total_simulated": len(vault_alphas),
                                "vault_alphas": vault_alphas
                            }, rf, indent=2)
                        log_msg("GroupA", f"Archived stats to groupa_results_{timestamp_str}.json")
                        log_msg("GroupA", f"Awaiting Antigravity to write 'groupa_generation_{generation}_alphas.json'...")
                        
                        # Wait for next generation file
                        target_file = os.path.join(alpha_maker_dir, f"groupa_generation_{generation}_alphas.json")
                        while not os.path.exists(target_file):
                            time.sleep(30)
                            
                        # Load and push to slots 1-4
                        with open(target_file, "r", encoding="utf-8") as f:
                            payload = json.load(f)
                            
                        log_msg("GroupA", f"Loaded {len(payload)} formulas. Overwriting queue on slots 1-4...")
                        ores = requests.post(f"{RENDER_URL}/api/overwrite-queue", headers=GROUPA_HEADERS, json=payload, timeout=30)
                        if ores.status_code == 200:
                            log_msg("GroupA", "[SUCCESS] Overwrote slots 1-4 successfully. Triggering simulation pipeline...")
                            requests.post(f"{RENDER_URL}/api/start-pipeline", headers=GROUPA_HEADERS, timeout=30)
                            generation += 1
            else:
                log_msg("GroupA", f"Queue status endpoint returned HTTP {r.status_code}")
        except Exception as e:
            log_msg("GroupA", f"Exception in loop: {e}")
        time.sleep(600)  # Check every 10 minutes

def group_b_loop():
    log_msg("GroupB", "Executor thread started (Slots 5-8)")
    alpha_maker_dir = os.path.join(AQL_ROOT, "alpha_maker")
    
    # Detect expected generation
    generation = 1
    try:
        files = os.listdir(alpha_maker_dir)
        gen_numbers = [int(m.group(1)) for f in files if (m := re.match(r"groupb_generation_(\d+)_alphas\.json", f))]
        if gen_numbers:
            generation = max(gen_numbers) + 1
    except Exception as e:
        log_msg("GroupB", f"Error checking generations: {e}")
        
    log_msg("GroupB", f"Next expected file: groupb_generation_{generation}_alphas.json")

    while True:
        try:
            # Query queue status from render server using Group B headers (Slots 5-8)
            url = f"{RENDER_URL}/api/queue-status"
            r = requests.get(url, headers=GROUPB_HEADERS, timeout=30)
            if r.status_code == 200:
                data = r.json()
                
                # Check for Group B pause/stop flags (if the endpoint returns active status)
                if data.get("pipeline_status") == "PAUSED":
                    log_msg("GroupB", "Group B execution is paused by operator. Standing by...")
                    time.sleep(30)
                    continue
                
                in_disk = data.get("queue_on_disk", 0)
                in_mem = data.get("in_memory", 0)
                pipeline_status = data.get("pipeline_status", "UNKNOWN")
                
                log_msg("GroupB", f"Queue status: Disk={in_disk} | In-Mem={in_mem} | State={pipeline_status}")
                
                if (in_disk == 0 and in_mem == 0) or pipeline_status == "COMPLETED":
                    log_msg("GroupB", "Slots 5-8 finished simulation. Querying statistics...")
                    
                    sr = requests.get(f"{RENDER_URL}/api/stats", headers=GROUPB_HEADERS, timeout=30)
                    if sr.status_code == 200:
                        vault_alphas = sr.json().get("vault_alphas", [])
                        
                        # Archive stats
                        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                        report_path = os.path.join(alpha_maker_dir, f"groupb_results_{timestamp_str}.json")
                        with open(report_path, "w", encoding="utf-8") as rf:
                            json.dump({
                                "timestamp": datetime.now().isoformat(),
                                "total_simulated": len(vault_alphas),
                                "vault_alphas": vault_alphas
                            }, rf, indent=2)
                        log_msg("GroupB", f"Archived stats to groupb_results_{timestamp_str}.json")
                        log_msg("GroupB", f"Awaiting Antigravity to write 'groupb_generation_{generation}_alphas.json'...")
                        
                        # Wait for next generation file
                        target_file = os.path.join(alpha_maker_dir, f"groupb_generation_{generation}_alphas.json")
                        while not os.path.exists(target_file):
                            time.sleep(30)
                            
                        # Load and push to slots 5-8
                        with open(target_file, "r", encoding="utf-8") as f:
                            payload = json.load(f)
                            
                        log_msg("GroupB", f"Loaded {len(payload)} formulas. Overwriting queue on slots 5-8...")
                        ores = requests.post(f"{RENDER_URL}/api/overwrite-queue", headers=GROUPB_HEADERS, json=payload, timeout=30)
                        if ores.status_code == 200:
                            log_msg("GroupB", "[SUCCESS] Overwrote slots 5-8 successfully. Triggering simulation pipeline...")
                            requests.post(f"{RENDER_URL}/api/start-pipeline", headers=GROUPB_HEADERS, timeout=30)
                            generation += 1
            else:
                log_msg("GroupB", f"Queue status endpoint returned HTTP {r.status_code}")
        except Exception as e:
            log_msg("GroupB", f"Exception in loop: {e}")
        time.sleep(600)  # Check every 10 minutes



if __name__ == "__main__":
    t1 = threading.Thread(target=group_a_loop)
    t2 = threading.Thread(target=group_b_loop)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()

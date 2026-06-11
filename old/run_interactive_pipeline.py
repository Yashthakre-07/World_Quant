import json
import os
import sys
import subprocess
import time
import re

def log_and_write(text):
    print(text)
    try:
        with open("live_run.txt", "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception:
        pass

def run_step(step_idx):
    log_and_write(f"\n==========================================")
    log_and_write(f"RUNNING STEP {step_idx}...")
    log_and_write(f"==========================================\n")
    
    script_path = f"scratch/execute_step_{step_idx}.py"
    if not os.path.exists(script_path):
        log_and_write(f"Script not found: {script_path}")
        return False
        
    cmd = [sys.executable, script_path]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    
    if result.stdout:
        log_and_write(result.stdout)
    if result.stderr:
        log_and_write("STDERR:")
        log_and_write(result.stderr)
        
    if result.returncode != 0:
        log_and_write(f"STEP {step_idx} failed with exit code {result.returncode}")
        return False
        
    log_and_write(f"STEP {step_idx} completed successfully.")
    return True

def sync_vault():
    log_and_write("\n==========================================")
    log_and_write("SYNCING REMOTE VAULTS TO LOCAL DB...")
    log_and_write("==========================================\n")
    sync_script = "developer/scratch_sync_vault_to_local.py"
    if os.path.exists(sync_script):
        cmd = [sys.executable, sync_script]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if res.stdout:
            log_and_write(res.stdout)
        if res.stderr:
            log_and_write(res.stderr)
    else:
        log_and_write(f"Sync script not found: {sync_script}")

def update_num_alphas(count):
    # Dynamically update NUM_ALPHAS inside execute_step_5.py
    step5_path = "scratch/execute_step_5.py"
    if os.path.exists(step5_path):
        try:
            with open(step5_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Replace NUM_ALPHAS = \d+ with NUM_ALPHAS = count
            updated = re.sub(r"NUM_ALPHAS\s*=\s*\d+", f"NUM_ALPHAS = {count}", content)
            with open(step5_path, "w", encoding="utf-8") as f:
                f.write(updated)
            log_and_write(f"Updated NUM_ALPHAS dynamically in execute_step_5.py to: {count}")
        except Exception as e:
            log_and_write(f"Error modifying execute_step_5.py: {e}")

def update_theme_datasets(datasets):
    # Overwrite theme_Dataset.json to filter Whitelisted Datasets
    if datasets:
        theme_list = [{"id": ds.strip()} for ds in datasets.split(",") if ds.strip()]
        try:
            with open("theme_Dataset.json", "w", encoding="utf-8") as f:
                json.dump(theme_list, f, indent=2)
            log_and_write(f"Updated theme_Dataset.json to filter datasets: {', '.join([d['id'] for d in theme_list])}")
        except Exception as e:
            log_and_write(f"Error writing theme_Dataset.json: {e}")
    else:
        log_and_write("No custom dataset filter specified. Using existing default theme datasets.")

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("==========================================================")
    print("WORLDQUANT BRAIN INTERACTIVE CUSTOM PIPELINE RUNNER")
    print("==========================================================")
    
    # 1. Ask for Target Group
    group_input = input("Enter target group (groupa/groupb) [default: groupa]: ").strip().lower()
    if group_input not in ["groupa", "groupb"]:
        group = "groupa"
    else:
        group = group_input
        
    # 2. Ask for Alpha Count
    alphas_input = input("Enter number of alphas to generate [default: 20]: ").strip()
    try:
        alpha_count = int(alphas_input) if alphas_input else 20
    except ValueError:
        alpha_count = 20
        
    # 3. Ask for Dataset Whitelists
    datasets_input = input("Enter datasets to whitelist (comma-separated, e.g. analyst4,analyst14) [default: all theme]: ").strip()
    
    # Clear live_run.txt at start of run
    try:
        with open("live_run.txt", "w", encoding="utf-8") as f:
            f.write(f"--- STARTING CUSTOM PIPELINE SEQUENCE FOR {group.upper()} at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            f.write(f"Configuration: Alphas={alpha_count} | Target Datasets={datasets_input or 'All Theme'}\n\n")
    except Exception:
        pass
        
    log_and_write(f"Selected Group: {group.upper()}")
    log_and_write(f"Selected Alpha Count: {alpha_count}")
    
    # Apply dynamic configurations
    update_num_alphas(alpha_count)
    update_theme_datasets(datasets_input)
    
    # Write starting state to pipeline_state.json
    state_path = "scratch/pipeline_state.json"
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump({"current_step": 0, "group": group}, f, indent=2)
        
    # Run database sync
    sync_vault()
    
    # Run steps 0 to 10
    for step in range(0, 11):
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump({"current_step": step, "group": group}, f, indent=2)
            
        success = run_step(step)
        if not success:
            log_and_write(f"Execution stopped at step {step}")
            sys.exit(1)
            
        next_step = 0 if step == 10 else step + 1
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump({"current_step": next_step, "group": group}, f, indent=2)
            
        time.sleep(1)

    log_and_write(f"\nALL 10 PIPELINE STEPS FOR {group.upper()} COMPLETED SUCCESSFULLY!")
    print(f"\nLive Run complete. All log output is saved in live_run.txt")

if __name__ == "__main__":
    main()

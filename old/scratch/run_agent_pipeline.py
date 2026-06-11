import json
import subprocess
import sys
import os
import time
import argparse

def run_step(step_idx):
    sys.stdout.reconfigure(encoding='utf-8')
    print(f"\n==========================================")
    print(f"RUNNING STEP {step_idx}...")
    print(f"==========================================\n")
    
    script_path = f"scratch/execute_step_{step_idx}.py"
    if not os.path.exists(script_path):
        print(f"Script not found: {script_path}")
        return False
        
    cmd = [sys.executable, script_path]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
        
    if result.returncode != 0:
        print(f"STEP {step_idx} failed with exit code {result.returncode}")
        return False
        
    print(f"STEP {step_idx} completed successfully.")
    return True

def sync_vault():
    sys.stdout.reconfigure(encoding='utf-8')
    print("\n==========================================")
    print("SYNCING REMOTE VAULTS TO LOCAL DB...")
    print("==========================================\n")
    sync_script = "developer/scratch_sync_vault_to_local.py"
    if os.path.exists(sync_script):
        cmd = [sys.executable, sync_script]
        subprocess.run(cmd, text=True, encoding="utf-8")
    else:
        print(f"Sync script not found: {sync_script}")

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    parser = argparse.ArgumentParser(description="Partial Executor for WQ Pipeline.")
    parser.add_argument("--part", type=int, choices=[1, 2, 3], required=True,
                        help="Part 1 (Steps 1-4), Part 2 (Steps 6-8), or Part 3 (Steps 8 recheck, 9-10)")
    
    args = parser.parse_args()
    
    state_path = "scratch/pipeline_state.json"
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
            group = state.get("group", "groupb")
    except Exception:
        group = "groupb"
        
    if args.part == 1:
        print(f"--- RUNNING PART 1 (STEPS 1-4) FOR {group.upper()} ---")
        sync_vault()
        steps = [1, 2, 3, 4]
    elif args.part == 2:
        print(f"--- RUNNING PART 2 (STEPS 6-8) FOR {group.upper()} ---")
        steps = [6, 7, 8]
    elif args.part == 3:
        print(f"--- RUNNING PART 3 (STEP 8 RECHECK & STEPS 9-10) FOR {group.upper()} ---")
        # Run Step 8 again to verify LLM refinements
        steps = [8, 9, 10]
        
    for step in steps:
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump({"current_step": step, "group": group}, f, indent=2)
            
        success = run_step(step)
        if not success:
            print(f"Execution stopped at step {step}")
            sys.exit(1)
            
        next_step = 0 if step == 10 else step + 1
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump({"current_step": next_step, "group": group}, f, indent=2)
            
        time.sleep(1)

    print(f"\nPART {args.part} COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()

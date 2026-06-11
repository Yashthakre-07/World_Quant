import json
import os
import sys
import subprocess
import time

def log_and_write(text):
    sys.stdout.reconfigure(encoding='utf-8')
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
        
    log_and_write(f"[STEP {step_idx} COMPLETED] - Step {step_idx} executed successfully.")
    return True

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 1. Reset/clear live_run.txt at start of trigger run
    try:
        with open("live_run.txt", "w", encoding="utf-8") as f:
            f.write(f"--- STARTING FRESH PIPELINE SEQUENCE FOR GROUP A at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n\n")
    except Exception as e:
        print(f"Error resetting live_run.txt: {e}")
        
    # Set starting state to step 0
    pipeline_state_path = "scratch/pipeline_state.json"
    with open(pipeline_state_path, "w", encoding="utf-8") as f:
        json.dump({"current_step": 0, "group": "groupa"}, f, indent=2)
        
    log_and_write("Starting sequence Steps 0 to 4...")
    
    for step in range(5):
        with open(pipeline_state_path, "w", encoding="utf-8") as f:
            json.dump({"current_step": step, "group": "groupa"}, f, indent=2)
            
        success = run_step(step)
        if not success:
            log_and_write(f"Execution stopped at step {step}")
            sys.exit(1)
            
        next_step = step + 1
        with open(pipeline_state_path, "w", encoding="utf-8") as f:
            json.dump({"current_step": next_step, "group": "groupa"}, f, indent=2)
            
        time.sleep(1)

    log_and_write("\nSTEPS 0 TO 4 SUCCESSFULLY COMPLETED!")

if __name__ == "__main__":
    main()

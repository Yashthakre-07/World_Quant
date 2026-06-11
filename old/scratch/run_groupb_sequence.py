import json
import subprocess
import sys
import os
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
        
    # Run the script
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

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Reset/clear live_run.txt at start of run
    try:
        with open("live_run.txt", "w", encoding="utf-8") as f:
            f.write(f"--- STARTING PIPELINE SEQUENCE FOR GROUP B at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n\n")
    except Exception:
        pass

    # Load current step from pipeline_state.json
    state_path = "scratch/pipeline_state.json"
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
            start_step = state.get("current_step", 0)
    except Exception:
        start_step = 0
        
    log_and_write(f"Starting execution of Group B from step: {start_step}")
    
    for step in range(start_step, 9):
        # Update pipeline_state.json with the current step we are about to run
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump({"current_step": step, "group": "groupb"}, f, indent=2)
            
        success = run_step(step)
        if not success:
            log_and_write(f"Execution stopped at step {step}")
            sys.exit(1)
            
        # Write the next step (incremented, wrapping to 0 after step 8)
        next_step = 0 if step == 8 else step + 1
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump({"current_step": next_step, "group": "groupb"}, f, indent=2)
            
        time.sleep(2) # brief pause between steps

    log_and_write("\nALL STEPS COMPLETED!")

if __name__ == "__main__":
    main()

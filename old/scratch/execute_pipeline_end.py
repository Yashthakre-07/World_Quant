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
        
    log_and_write(f"STEP {step_idx} completed successfully.")
    return True

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    log_and_write("\n--- CONTINUOUS PIPELINE SEQUENCE FROM STEP 5 ---")
    
    # 1. Step 5 Archiving and State Increment
    state_path = "scratch/generation_state.json"
    gen = 6
    if os.path.exists(state_path):
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
                gen = state.get("current_generation", 6)
        except Exception as e:
            log_and_write(f"Error loading generation state: {e}")
    
    log_and_write(f"Archiving generated alphas for generation {gen}...")
    
    # Read generated alphas
    gen_alphas_path = "scratch/generated_alphas.json"
    if os.path.exists(gen_alphas_path):
        try:
            with open(gen_alphas_path, "r", encoding="utf-8") as f:
                alphas = json.load(f)
            
            # Save to generation specific archive
            archive_path = f"scratch/groupa_generation_{gen}.json"
            with open(archive_path, "w", encoding="utf-8") as f:
                json.dump(alphas, f, indent=2)
            log_and_write(f"Archived to {archive_path}")
            
            # Update generation state
            state["current_generation"] = gen + 1
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            log_and_write(f"Generation state incremented to {gen + 1}")
        except Exception as e:
            log_and_write(f"Error during Step 5 archiving: {e}")
            sys.exit(1)
    else:
        log_and_write(f"Error: {gen_alphas_path} does not exist!")
        sys.exit(1)

    # Update pipeline state to Step 6
    pipeline_state_path = "scratch/pipeline_state.json"
    with open(pipeline_state_path, "w", encoding="utf-8") as f:
        json.dump({"current_step": 6, "group": "groupa"}, f, indent=2)

    # 2. Sequential Execution of Steps 6 to 10
    for step in range(6, 11):
        with open(pipeline_state_path, "w", encoding="utf-8") as f:
            json.dump({"current_step": step, "group": "groupa"}, f, indent=2)
            
        success = run_step(step)
        if not success:
            log_and_write(f"Execution stopped at step {step}")
            sys.exit(1)
            
        next_step = 0 if step == 10 else step + 1
        with open(pipeline_state_path, "w", encoding="utf-8") as f:
            json.dump({"current_step": next_step, "group": "groupa"}, f, indent=2)
            
        time.sleep(1)

    log_and_write("\nALL RESUMED STEPS COMPLETED!")

if __name__ == "__main__":
    main()

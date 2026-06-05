import os
import sys
import time

def run_step_sequentially():
    sys.stdout.reconfigure(encoding='utf-8')
    steps_dir = "master_prompt"
    
    # We will step through 0 to 10
    for i in range(11):
        file_path = os.path.join(steps_dir, f"step_{i}.md")
        if not os.path.exists(file_path):
            continue
            
        print(f"\n==========================================")
        print(f"⌛ STARTING STEP {i}...")
        print(f"==========================================\n")
        
        # Read and display the instruction for this step
        with open(file_path, "r", encoding="utf-8") as f:
            instruction = f.read()
            print(instruction)
            
        print(f"\n==========================================")
        input(f"👉 Press ENTER to complete STEP {i} and proceed to the next step...")
        print(f"==========================================\n")
        
        # Give a small pause to stabilize
        time.sleep(1)

if __name__ == "__main__":
    try:
        run_step_sequentially()
    except KeyboardInterrupt:
        print("\nSequential execution halted.")

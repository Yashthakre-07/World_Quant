import os
import time
import sys

def feed_steps():
    # Reconfigure stdout to use utf-8 to prevent encoding errors in Windows terminal
    sys.stdout.reconfigure(encoding='utf-8')
    steps_dir = "master_prompt"
    for i in range(11):
        file_path = os.path.join(steps_dir, f"step_{i}.md")
        if os.path.exists(file_path):
            print(f"\n=== START OF STEP {i} ===")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                print(content)
            print(f"=== END OF STEP {i} ===\n")
            # Give a small pause to simulate step-by-step feeding
            time.sleep(1)

if __name__ == "__main__":
    feed_steps()

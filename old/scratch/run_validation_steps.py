import subprocess
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
steps = [6, 7, 8, 9, 10]
python_path = sys.executable

for step in steps:
    print("\n" + "="*60)
    print(f"RUNNING STEP {step}...")
    print("="*60)
    script = f"scratch/execute_step_{step}.py"
    if os.path.exists(script):
        result = subprocess.run([python_path, script], capture_output=True, text=True, encoding="utf-8")
        # Print safely
        safe_out = result.stdout.encode('utf-8', errors='replace').decode('utf-8')
        print(safe_out)
        if result.stderr:
            safe_err = result.stderr.encode('utf-8', errors='replace').decode('utf-8')
            print("STDERR:")
            print(safe_err)
        if result.returncode != 0:
            print(f"Step {step} failed with exit code {result.returncode}")
            sys.exit(1)
    else:
        print(f"Script not found: {script}")
        sys.exit(1)

print("\nALL STEPS COMPLETED SUCCESSFULLY!")

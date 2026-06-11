import os
import shutil
from pathlib import Path

# Paths
WQ_ROOT = Path("C:/Users/Admin/Documents/VIBE_YT/wq").resolve()
OLD_DIR = WQ_ROOT / "old"
OLD_SCRATCH_DIR = OLD_DIR / "scratch"

# Whitelists of files to KEEP in their current locations
ROOT_KEEP = {
    "run_pipeline.py",
    "run_trigger.py",
    "run_sequential_steps.py",
    "sai.env",
    "yash.env",
    "session_json.txt",
    "live_run.txt",
    "trigger.md",
    "instructions.md",
    "alpha_generation_guide.md",
    "groupa.md",
    "groupb.md",
    "run.bat",
    "run.ps1",
    "requirements.txt",
    ".gitignore",
    ".git",
    "src",
    "db",
    "documentation",
    "old",
    "scratch",
    "alphas",
    "alphas_dataset",
    "__pycache__",
    "developer",
    "alpha_maker",
    "master_prompt",
    "static",
    "app.py",
    "Procfile",
    "render.yaml"
}

SCRATCH_KEEP = {
    "execute_step_0.py",
    "execute_step_1.py",
    "execute_step_2.py",
    "execute_step_3.py",
    "execute_step_4.py",
    "execute_step_5.py",
    "execute_step_5_wrap.py",
    "execute_step_5_groupb.py",
    "execute_step_6.py",
    "execute_step_7.py",
    "execute_step_8.py",
    "execute_step_9.py",
    "execute_step_10.py",
    "show_active_alphas.py",
    "fix_generated_alphas.py",
    "fix_local_auth.py",
    "check_db_errors_real.py",
    "check_local_pipeline_status.py",
    "check_queue_status_now.py",
    "slot_status_report.md",
    "generation_state.json",
    "discovered_whitelists.json",
    "elite_templates.json",
    "pipeline_state.json",
    "analyst_fields",
    "analyst_fields_sai",
    "selected_analyst_fields",
    "__pycache__"
}

def main():
    print(f"Starting workspace cleanup inside: {WQ_ROOT}")
    
    # 1. Create old directories
    OLD_DIR.mkdir(exist_ok=True)
    OLD_SCRATCH_DIR.mkdir(exist_ok=True)
    
    # 2. Process root directory
    print("\n--- Processing Root Directory ---")
    for item in WQ_ROOT.iterdir():
        if item.name in ROOT_KEEP:
            continue
        
        target = OLD_DIR / item.name
        print(f"Moving root item: {item.name} -> old/{item.name}")
        try:
            shutil.move(str(item), str(target))
        except Exception as e:
            print(f"Error moving {item.name}: {e}")
            
    # 3. Process scratch directory
    print("\n--- Processing Scratch Directory ---")
    scratch_path = WQ_ROOT / "scratch"
    if scratch_path.exists():
        for item in scratch_path.iterdir():
            if item.name in SCRATCH_KEEP:
                continue
            
            target = OLD_SCRATCH_DIR / item.name
            print(f"Moving scratch item: {item.name} -> old/scratch/{item.name}")
            try:
                shutil.move(str(item), str(target))
            except Exception as e:
                print(f"Error moving {item.name}: {e}")
                
    print("\nWorkspace cleanup complete! Legacy files archived in wq/old/.")

if __name__ == "__main__":
    main()

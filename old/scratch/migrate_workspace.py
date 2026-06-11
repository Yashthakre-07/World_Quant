import os
import shutil
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent
    imp_dir = root / "imp"
    old_dir = root / "old"
    
    # 1. Create target directories
    print("Creating target directories...")
    imp_dir.mkdir(exist_ok=True)
    old_dir.mkdir(exist_ok=True)
    
    # Define active list (to go into imp/)
    active_root_files = [
        "run_pipeline.py",
        "run_trigger.py",
        "run_sequential_steps.py",
        "sai.env",
        "yash.env",
        "session_json.txt",
        "trigger.md",
        "instructions.md",
        "alpha_generation_guide.md",
        "groupa.md",
        "groupb.md",
        "live_run.txt",
        ".env"
    ]
    
    active_dirs = [
        "src",
        "db"
    ]
    
    active_scratch_files = [
        "execute_step_0.py",
        "execute_step_1.py",
        "execute_step_2.py",
        "execute_step_3.py",
        "execute_step_4.py",
        "execute_step_5.py",
        "execute_step_5_wrap.py",
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
        "generation_state.json"
    ]

    # Create scratch folder inside imp/
    imp_scratch = imp_dir / "scratch"
    imp_scratch.mkdir(exist_ok=True)
    
    # 2. Move active files to imp/
    print("\nMoving active root files...")
    for filename in active_root_files:
        src_file = root / filename
        if src_file.exists():
            shutil.move(str(src_file), str(imp_dir / filename))
            print(f"Moved {filename} to imp/")
            
    print("\nMoving active directories...")
    for dirname in active_dirs:
        src_path = root / dirname
        if src_path.exists():
            # If target exists, merge or remove target first
            target_path = imp_dir / dirname
            if target_path.exists():
                shutil.rmtree(str(target_path))
            shutil.move(str(src_path), str(target_path))
            print(f"Moved directory {dirname} to imp/")
            
    print("\nMoving active scratch files...")
    scratch_dir = root / "scratch"
    if scratch_dir.exists():
        for filename in active_scratch_files:
            src_file = scratch_dir / filename
            if src_file.exists():
                shutil.move(str(src_file), str(imp_scratch / filename))
                print(f"Moved scratch/{filename} to imp/scratch/")
                
    # 3. Archive everything else to old/
    print("\nArchiving remaining files and directories to old/...")
    # List files in root
    for entry in root.iterdir():
        name = entry.name
        # Do not move .git, .gitignore, imp, old, run.bat, run.ps1, or the migration script itself
        if name in (".git", ".gitignore", "imp", "old", "run.bat", "run.ps1", "migrate_workspace.py"):
            continue
            
        target_path = old_dir / name
        if target_path.exists():
            if target_path.is_dir():
                shutil.rmtree(str(target_path))
            else:
                target_path.unlink()
                
        shutil.move(str(entry), str(target_path))
        print(f"Archived {name} to old/")
        
    print("\nMigration complete!")

if __name__ == '__main__':
    main()

import os
import shutil
from pathlib import Path

# Paths
workspace_dir = Path("c:/Users/Admin/Documents/VIBE_YT/wq")
dev_dir = workspace_dir / "developer"
doc_dir = workspace_dir / "documentation"

def main():
    # 1. Create developer folder
    dev_dir.mkdir(exist_ok=True)
    print(f"Created developer folder at: {dev_dir}")
    
    # 2. Define list of files to stay in root
    # Essential server/build files & readable documentation
    essential_files = {
        "app.py",
        "run_pipeline.py",
        "requirements.txt",
        "Procfile",
        "render.yaml",
        "sai.env",
        "yash.env",
        "README.md",
        "research.md",
        "instructions.md",
        "dataset.md",
        "ACE API [Gold].zip",
        ".gitignore",
        ".git",
        ".env.example"
    }

    # 3. Define folders to stay in root
    essential_dirs = {
        "alphas",
        "db",
        "documentation",
        "src",
        "static",
        "developer"
    }

    # 4. Iterate root contents
    for item in workspace_dir.iterdir():
        name = item.name
        
        # Skip if it is essential
        if name in essential_files or name in essential_dirs or name.startswith(".git"):
            continue
            
        # Move extracted ACE API folder to documentation directory
        if name == "ace_api_extracted":
            target = doc_dir / "ace_api_extracted"
            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(item), str(target))
            print(f"Moved {name} -> documentation/ace_api_extracted")
            continue
            
        # Move everything else (scratch files, developer scripts, local report logs) to developer folder
        if item.is_file():
            target = dev_dir / name
            shutil.move(str(item), str(target))
            print(f"Moved file: {name} -> developer/{name}")
        elif item.is_dir() and name not in essential_dirs:
            target = dev_dir / name
            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(item), str(target))
            print(f"Moved folder: {name} -> developer/{name}")

    print("\nWorkspace successfully cleaned up and organized!")

if __name__ == "__main__":
    main()

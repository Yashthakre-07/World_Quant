import os

notebook_path = "c:/Users/Admin/Documents/VIBE_YT/wq/documentation/ace_api_extracted/how_to_use.ipynb"
if os.path.exists(notebook_path):
    with open(notebook_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_text = f.read()
    print(f"Raw notebook length: {len(raw_text)}")
    print(f"Occurrences of 'event': {raw_text.lower().count('event')}")
    print(f"Occurrences of 'sparse': {raw_text.lower().count('sparse')}")
    print(f"Occurrences of 'analyst': {raw_text.lower().count('analyst')}")
    print(f"Occurrences of 'anl4': {raw_text.lower().count('anl4')}")
else:
    print("Notebook not found")

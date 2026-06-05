import json
import os

notebook_path = "c:/Users/Admin/Documents/VIBE_YT/wq/documentation/ace_api_extracted/how_to_use.ipynb"
if os.path.exists(notebook_path):
    with open(notebook_path, "r", encoding="utf-8", errors="ignore") as f:
        notebook = json.load(f)
    
    cells = notebook.get("cells", [])
    print(f"Total cells in notebook: {len(cells)}")
    
    count = 0
    for cell_idx, cell in enumerate(cells):
        source = "".join(cell.get("source", []))
        # Search for keywords
        if any(x in source.lower() for x in ["event", "sparse", "timeline"]):
            count += 1
            print(f"\n--- Matched Cell #{count} (Index {cell_idx}, Type {cell.get('cell_type')}) ---")
            print(source[:400])
            print("-" * 50)
            if count >= 15:
                break
else:
    print(f"Notebook not found: {notebook_path}")

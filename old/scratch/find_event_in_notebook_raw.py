import json
import os

notebook_path = "c:/Users/Admin/Documents/VIBE_YT/wq/documentation/ace_api_extracted/how_to_use.ipynb"
with open(notebook_path, "r", encoding="utf-8", errors="ignore") as f:
    data = json.load(f)

cells = data.get("cells", [])
count = 0
for idx, cell in enumerate(cells):
    source = cell.get("source", [])
    source_text = "".join(source)
    if "event" in source_text.lower() or "sparse" in source_text.lower():
        count += 1
        print(f"\nCell {idx} ({cell.get('cell_type')}):")
        # Print lines in source containing the keywords
        for line in source:
            if any(w in line.lower() for w in ["event", "sparse"]):
                print(f"  > {line.strip()[:150]}")
        if count >= 10:
            break

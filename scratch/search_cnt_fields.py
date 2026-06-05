import json
import os

wq_root = "c:/Users/Admin/Documents/VIBE_YT/wq"

# Search for any fields containing "cnt", "count", "up", "down", "num" in analyst14 fields.json
fields_path = os.path.join(wq_root, "alphas_dataset", "analyst14", "alphas", "fields.json")
if os.path.exists(fields_path):
    with open(fields_path, "r", encoding="utf-8") as f:
        fields = json.load(f)
    print(f"Total analyst14 fields: {len(fields)}")
    matched = [f for f in fields if any(x in f.get("id", "").lower() for x in ["cnt", "count", "up", "down", "num"])]
    print(f"Matched fields ({len(matched)}):")
    for f in matched[:40]:
        print(f"ID: {f.get('id')} | Name: {f.get('name')}")
else:
    print(f"Path not found: {fields_path}")

import os
import json
import glob

# Search for any fields containing "cnt", "up", "down", "rev", "rec" in their IDs
target_patterns = ["cnt", "up", "down", "rev", "rec", "estimate", "count"]

for path in glob.glob("scratch/selected_analyst_fields/*.json") + glob.glob("scratch/analyst_fields_sai/*.json"):
    filename = os.path.basename(path)
    if "analyst10" in filename or "analyst14" in filename or "analyst15" in filename:
        try:
            with open(path, "r") as f:
                data = json.load(f)
                matches = []
                for item in data:
                    fid = item.get("id", "").lower()
                    # Check if any of our search patterns match
                    if any(pat in fid for pat in target_patterns):
                        matches.append(item.get("id"))
                if matches:
                    print(f"Dataset {filename}: found {len(matches)} matching fields. Examples:")
                    print(matches[:30])
                    print("=" * 50)
        except Exception as e:
            print(f"Error reading {path}: {e}")

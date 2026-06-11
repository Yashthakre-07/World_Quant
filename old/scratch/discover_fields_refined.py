import os
import json
import glob

# Search in the folders for JSON files matching the dataset ID exactly
target_datasets = ["analyst14", "analyst16", "analyst4", "analyst44", "analyst45"]
results = {d: [] for d in target_datasets}

for path in glob.glob("scratch/selected_analyst_fields/*.json") + glob.glob("scratch/analyst_fields_sai/*.json"):
    filename = os.path.basename(path)
    # Check exact match or prefix
    # e.g., analyst14_fields.json -> analyst14
    for ds in target_datasets:
        if filename.startswith(ds + "_"):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    for item in data:
                        results[ds].append(item.get("id"))
            except Exception as e:
                print(f"Error reading {path}: {e}")

for ds, fields in results.items():
    print(f"Dataset {ds}: {len(fields)} fields found. Examples:")
    print(fields[:15])
    print("-" * 40)

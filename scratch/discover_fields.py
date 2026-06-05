import os
import json
import glob

target_datasets = ["analyst14", "analyst16", "analyst4", "analyst44", "analyst45"]
results = {d: [] for d in target_datasets}

# Scan selected_analyst_fields/
for path in glob.glob("scratch/selected_analyst_fields/*.json"):
    filename = os.path.basename(path)
    for ds in target_datasets:
        if ds in filename:
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    for item in data:
                        results[ds].append(item.get("id"))
            except Exception as e:
                print(f"Error reading {path}: {e}")

# Scan analyst_fields_sai/
for path in glob.glob("scratch/analyst_fields_sai/*.json"):
    filename = os.path.basename(path)
    for ds in target_datasets:
        if ds in filename:
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    for item in data:
                        results[ds].append(item.get("id"))
            except Exception as e:
                print(f"Error reading {path}: {e}")

# Search inside available_datasets.json if any of the target datasets are present but didn't have their own file
try:
    with open("scratch/analyst_fields_sai/available_datasets.json", "r") as f:
        data = json.load(f)
        # Check if fields are inside this list
        # available_datasets.json contains dataset metadata, but maybe fields are listed?
except Exception:
    pass

for ds, fields in results.items():
    print(f"Dataset {ds}: {len(fields)} fields found. Examples:")
    print(fields[:10])
    print("-" * 40)

import os
import json

wq_root = "c:/Users/Admin/Documents/VIBE_YT/wq"
alphas_dataset_dir = os.path.join(wq_root, "alphas_dataset")

for dataset in ["analyst4", "analyst14", "analyst16", "analyst44", "analyst45"]:
    fields_path = os.path.join(alphas_dataset_dir, dataset, "alphas", "fields.json")
    if os.path.exists(fields_path):
        with open(fields_path, "r", encoding="utf-8") as f:
            fields = json.load(f)
        print(f"Dataset: {dataset} | Total fields: {len(fields)}")
        print(f"Sample fields:")
        for f in fields[:10]:
            print(f"  * {f.get('id')} - {f.get('name')}")
    else:
        print(f"Dataset: {dataset} | fields.json not found")

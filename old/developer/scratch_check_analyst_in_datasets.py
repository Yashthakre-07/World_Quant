import json

try:
    with open("documentation/dataset/raw_datasets.json", "r") as f:
        datasets = json.load(f)
    print(f"Total datasets in raw cache: {len(datasets)}")
    analyst_datasets = [d for d in datasets if "analyst" in d.get("id", "")]
    print(f"Total Analyst Datasets: {len(analyst_datasets)}")
    for d in analyst_datasets:
        print(f"  - ID: {d.get('id')} | Name: {d.get('name')}")
except Exception as e:
    print(f"Error: {e}")

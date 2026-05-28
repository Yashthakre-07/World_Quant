import json

try:
    with open("mapped_mfm_fields.json", "r") as f:
        fields = json.load(f)
    print(f"Total fields in mapped_mfm_fields.json: {len(fields)}")
    
    analyst_fields = [f for f in fields if f.get("category") == "Analyst"]
    print(f"Total Analyst fields: {len(analyst_fields)}")
    
    unique_datasets = {}
    for f in analyst_fields:
        ds = f.get("dataset")
        if ds not in unique_datasets:
            unique_datasets[ds] = {
                "sample_field": f.get("id"),
                "desc": f.get("description"),
                "count": 0
            }
        unique_datasets[ds]["count"] += 1
        
    print("\nUnique Analyst Datasets in mapped_mfm_fields.json:")
    for ds, info in unique_datasets.items():
        print(f"  - Dataset ID/Name: {ds} | Fields count: {info['count']} | Sample field: {info['sample_field']} ({info['desc']})")
except Exception as e:
    print(f"Error: {e}")

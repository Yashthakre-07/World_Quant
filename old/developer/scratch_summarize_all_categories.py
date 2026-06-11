import json
from pathlib import Path

def main():
    file_path = Path("documentation/dataset/all_datasets.json")
    if not file_path.exists():
        print("all_datasets.json not found.")
        return
        
    print(f"Loading master catalog: {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)
        
    print(f"Master catalog categories: {list(catalog.keys())}")
    
    summary = {}
    for cat_name, cat_data in catalog.items():
        datasets = cat_data.get("datasets", [])
        num_ds = len(datasets)
        num_fields = sum(len(d.get("fields", [])) for d in datasets)
        
        # Collect sample fields
        sample_fields = []
        for d in datasets:
            for f in d.get("fields", [])[:2]:
                sample_fields.append(f"{f.get('id')} ({f.get('description')[:40]}...)")
            if len(sample_fields) >= 4:
                break
                
        summary[cat_name] = {
            "datasets_count": num_ds,
            "fields_count": num_fields,
            "samples": sample_fields[:4]
        }
        
    print("\nLocal Catalog Category Summary:")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()

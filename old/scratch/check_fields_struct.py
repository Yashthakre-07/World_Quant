import json

all_datasets_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\documentation\dataset\all_datasets.json"

with open(all_datasets_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for category, cat_data in data.items():
    print(f"\nCategory: {category}")
    datasets = cat_data.get('datasets', {})
    print(f"Type of datasets: {type(datasets)}")
    if isinstance(datasets, dict):
        print(f"Number of datasets: {len(datasets)}")
        print(f"Sample dataset keys: {list(datasets.keys())[:5]}")
        first_key = list(datasets.keys())[0] if datasets else None
        if first_key:
            sample_ds = datasets[first_key]
            print(f"Sample dataset '{first_key}' keys: {list(sample_ds.keys())}")
            # check fields structure
            fields = sample_ds.get('fields', [])
            print(f"Fields type: {type(fields)}")
            if isinstance(fields, dict):
                print(f"Number of fields: {len(fields)}")
                print(f"Sample field keys: {list(fields.keys())[:3]}")
                first_field_key = list(fields.keys())[0] if fields else None
                if first_field_key:
                    print(f"Sample field data: {fields[first_field_key]}")
            elif isinstance(fields, list):
                print(f"Number of fields: {len(fields)}")
                if fields:
                    print(f"Sample field data: {fields[0]}")
    elif isinstance(datasets, list):
        print(f"Number of datasets: {len(datasets)}")
        if datasets:
            print(f"Sample dataset keys: {list(datasets[0].keys())}")
            fields = datasets[0].get('fields', [])
            print(f"Fields type: {type(fields)}")
            if fields:
                print(f"Sample field data: {fields[0]}")

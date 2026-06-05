import os
import json

doc_dir = r"c:\Users\Admin\Documents\VIBE_YT\wq\documentation\dataset"
category_files = [f for f in os.listdir(doc_dir) if f.startswith('category_') and f.endswith('.json')]

all_found = {}

for cf in category_files:
    path = os.path.join(doc_dir, cf)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check structure
        datasets_list = []
        if isinstance(data, list):
            datasets_list = data
        elif isinstance(data, dict):
            datasets_list = data.get('datasets', [])
            if not datasets_list:
                # sometimes it might be list under a key
                for k, v in data.items():
                    if isinstance(v, list):
                        datasets_list = v
                        break
        
        for ds in datasets_list:
            if isinstance(ds, dict) and 'id' in ds:
                fields_list = ds.get('fields', [])
                all_found[ds['id']] = {
                    'name': ds.get('name'),
                    'file': cf,
                    'fields_count': len(fields_list),
                    'has_fields': len(fields_list) > 0,
                    'has_desc': any(f.get('description') for f in fields_list) if isinstance(fields_list, list) else False,
                    'has_use': any('alphaCount' in f for f in fields_list) if isinstance(fields_list, list) else False
                }
    except Exception as e:
        print(f"Error reading {cf}: {e}")

print(f"Found {len(all_found)} unique datasets in category files.")

# Also check raw_datasets.json
raw_ds_path = os.path.join(doc_dir, 'raw_datasets.json')
if os.path.exists(raw_ds_path):
    try:
        with open(raw_ds_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        print(f"raw_datasets.json type: {type(raw_data)}")
        if isinstance(raw_data, list):
            print(f"raw_datasets.json datasets: {len(raw_data)}")
            for ds in raw_data:
                if isinstance(ds, dict) and 'id' in ds:
                    if ds['id'] not in all_found:
                        all_found[ds['id']] = {
                            'name': ds.get('name'),
                            'file': 'raw_datasets.json',
                            'fields_count': 0,
                            'has_fields': False,
                            'has_desc': False,
                            'has_use': False
                        }
    except Exception as e:
         print(f"Error reading raw_datasets.json: {e}")

# Check coverage of 42 theme datasets
theme_json_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\theme_Dataset.json"
with open(theme_json_path, 'r', encoding='utf-8') as f:
    theme_datasets = json.load(f)

print("\n--- Theme Dataset Coverage ---")
missing = []
for ds in theme_datasets:
    ds_id = ds['id']
    if ds_id in all_found:
        info = all_found[ds_id]
        print(f"{ds_id}: Found in {info['file']}, fields={info['fields_count']}, has_desc={info['has_desc']}, has_use={info['has_use']}")
    else:
        missing.append(ds_id)

print(f"\nMissing {len(missing)} datasets in category/raw json files:")
print(missing)

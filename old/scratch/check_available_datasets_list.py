import json
import os

path = r"c:\Users\Admin\Documents\VIBE_YT\wq\scratch\analyst_fields_sai\available_datasets.json"
theme_json_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\theme_Dataset.json"

with open(theme_json_path, 'r', encoding='utf-8') as f:
    theme_datasets = json.load(f)
theme_ids = {d['id'] for d in theme_datasets}

if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Loaded available_datasets.json. Type: {type(data)}, length: {len(data)}")
    
    # Check if theme datasets are in this available list
    found_datasets = {}
    for ds in data:
        ds_id = ds.get('id')
        if ds_id in theme_ids:
            found_datasets[ds_id] = {
                'name': ds.get('name'),
                'fieldCount': ds.get('fieldCount'),
                'userCount': ds.get('userCount'),
                'alphaCount': ds.get('alphaCount')
            }
            
    print(f"Found {len(found_datasets)} out of {len(theme_ids)} theme datasets in available_datasets.json:")
    for ds_id, info in sorted(found_datasets.items()):
        print(f"  {ds_id}: fields={info['fieldCount']}, userCount={info['userCount']}, alphaCount={info['alphaCount']}")
        
    missing = theme_ids - set(found_datasets.keys())
    print(f"\nMissing from available_datasets.json ({len(missing)}):")
    print(sorted(list(missing)))
else:
    print("available_datasets.json does not exist.")

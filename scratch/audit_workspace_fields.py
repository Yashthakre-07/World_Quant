import os
import json

theme_json_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\theme_Dataset.json"
workspace_dir = r"c:\Users\Admin\Documents\VIBE_YT\wq"

with open(theme_json_path, 'r', encoding='utf-8') as f:
    theme_datasets = json.load(f)

theme_ids = {d['id'] for d in theme_datasets}

# Search the entire workspace for files named <dataset_id>_fields.json or similar
found_field_files = {}

for root, dirs, files in os.walk(workspace_dir):
    for file in files:
        if file.endswith('_fields.json') or file.endswith('_fields_all.json'):
            # Extract dataset ID
            base = file.replace('_fields_all.json', '').replace('_fields.json', '')
            if base in theme_ids:
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        fields_data = json.load(f)
                    
                    count = len(fields_data) if isinstance(fields_data, list) else 0
                    has_desc = False
                    has_use = False
                    if count > 0 and isinstance(fields_data, list):
                        has_desc = any(f.get('description') for f in fields_data)
                        has_use = any('alphaCount' in f or 'userCount' in f for f in fields_data)
                    
                    found_field_files[base] = {
                        'path': path,
                        'count': count,
                        'has_desc': has_desc,
                        'has_use': has_use
                    }
                except Exception as e:
                    print(f"Error reading {file}: {e}")

# Check files under other directories, for example catalog
# The catalog has some datasets in category_*.json files
catalog_dir = r"c:\Users\Admin\Documents\VIBE_YT\wq\documentation\dataset"
category_files = [f for f in os.listdir(catalog_dir) if f.startswith('category_') and f.endswith('.json')]
for cf in category_files:
    path = os.path.join(catalog_dir, cf)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        datasets_list = data.get('datasets', []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        for ds in datasets_list:
            ds_id = ds.get('id')
            if ds_id in theme_ids:
                fields_list = ds.get('fields', [])
                count = len(fields_list)
                has_desc = any(f.get('description') for f in fields_list) if count > 0 else False
                has_use = any('alphaCount' in f for f in fields_list) if count > 0 else False
                
                # If already found in individual file, keep that or update if catalog has more fields
                if ds_id not in found_field_files or found_field_files[ds_id]['count'] < count:
                    found_field_files[ds_id] = {
                        'path': path,
                        'count': count,
                        'has_desc': has_desc,
                        'has_use': has_use
                    }
    except Exception as e:
        pass

print("\n--- DATASET FIELD DETAILS COVERAGE ---")
fully_present = []
missing_details = []

for ds in theme_datasets:
    ds_id = ds['id']
    if ds_id in found_field_files:
        info = found_field_files[ds_id]
        print(f"[OK] {ds_id:15s}: Found fields={info['count']}, has_description={info['has_desc']}, has_usage={info['has_use']} (Source: {os.path.basename(info['path'])})")
        fully_present.append(ds_id)
    else:
        print(f"[MISSING] {ds_id:15s}: NO field details found locally.")
        missing_details.append(ds_id)

print(f"\nSummary: {len(fully_present)} datasets have field details locally, {len(missing_details)} do not.")
print("Missing datasets list:")
print(missing_details)

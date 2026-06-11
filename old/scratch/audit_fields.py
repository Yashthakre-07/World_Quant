import os
import json

# Paths
theme_json_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\theme_Dataset.json"
all_datasets_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\documentation\dataset\all_datasets.json"
selected_fields_dir = r"c:\Users\Admin\Documents\VIBE_YT\wq\scratch\selected_analyst_fields"

# Load theme datasets
with open(theme_json_path, 'r', encoding='utf-8') as f:
    theme_datasets = json.load(f)

theme_ids = [d['id'] for d in theme_datasets]
print(f"Loaded {len(theme_ids)} theme datasets.")

# Load all datasets from catalog
all_ds_data = {}
if os.path.exists(all_datasets_path):
    try:
        with open(all_datasets_path, 'r', encoding='utf-8') as f:
            all_ds_data = json.load(f)
        print("Loaded all_datasets.json successfully.")
    except Exception as e:
        print(f"Error loading all_datasets.json: {e}")

# Check which categories and IDs exist in all_datasets.json
available_in_catalog = {}
# all_datasets.json is structured by category dict: {'name': category, 'datasets': list of datasets}
for category, cat_data in all_ds_data.items():
    datasets_list = cat_data.get('datasets', [])
    for ds in datasets_list:
        if 'id' in ds:
            fields_list = ds.get('fields', [])
            available_in_catalog[ds['id']] = {
                'name': ds.get('name'),
                'category': category,
                'fields_count': len(fields_list),
                'fields': fields_list
            }

print(f"Found {len(available_in_catalog)} datasets in all_datasets.json catalog.")

# Check locally downloaded specific field files in selected_fields_dir
local_files = os.listdir(selected_fields_dir) if os.path.exists(selected_fields_dir) else []
local_field_datasets = {}
for fn in local_files:
    if fn.endswith('_fields.json'):
        ds_id = fn.replace('_fields.json', '')
        path = os.path.join(selected_fields_dir, fn)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                fields_data = json.load(f)
            local_field_datasets[ds_id] = len(fields_data) if isinstance(fields_data, list) else 0
        except Exception as e:
            local_field_datasets[ds_id] = f"Error: {e}"

# Build a comprehensive status list
audit_results = []
for ds in theme_datasets:
    ds_id = ds['id']
    in_catalog = ds_id in available_in_catalog
    catalog_fields = available_in_catalog[ds_id]['fields_count'] if in_catalog else 0
    
    # Check if we have fields download
    downloaded_count = local_field_datasets.get(ds_id, 0)
    
    # Check if fields have description and usage (alphaCount)
    has_description = False
    has_usage = False
    if in_catalog and catalog_fields > 0:
        fields = available_in_catalog[ds_id]['fields']
        has_description = any(f.get('description') for f in fields)
        has_usage = any('alphaCount' in f for f in fields)
    
    audit_results.append({
        'id': ds_id,
        'name': ds['name'],
        'category': ds['category'],
        'in_catalog': in_catalog,
        'catalog_fields_count': catalog_fields,
        'downloaded_count': downloaded_count,
        'has_description': has_description,
        'has_usage': has_usage
    })

# Output results to a JSON file for analysis
output_audit_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\scratch\theme_dataset_audit.json"
with open(output_audit_path, 'w', encoding='utf-8') as f:
    json.dump(audit_results, f, indent=2)

print(f"Audit completed. Results saved to {output_audit_path}")
for res in audit_results:
    print(f"{res['id']}: in_catalog={res['in_catalog']}, catalog_fields={res['catalog_fields_count']}, downloaded={res['downloaded_count']}, has_desc={res['has_description']}, has_use={res['has_usage']}")

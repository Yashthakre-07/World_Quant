import os
import json
import sqlite3

# Paths
theme_json_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\theme_Dataset.json"
db_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\db\alpha_vault.db"
ad_dir = r"c:\Users\Admin\Documents\VIBE_YT\wq\alphas_dataset"
selected_fields_dir = r"c:\Users\Admin\Documents\VIBE_YT\wq\scratch\selected_analyst_fields"

with open(theme_json_path, 'r', encoding='utf-8') as f:
    theme_datasets = json.load(f)

# 1. Fetch counts from sqlite db
db_counts = {}
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT dataset, COUNT(*) FROM whitelisted_variables GROUP BY dataset")
        rows = cursor.fetchall()
        for row in rows:
            db_counts[row[0].lower().replace('_', '')] = row[1]
        conn.close()
    except Exception as e:
        print(f"Error querying SQL database: {e}")

# 2. Fetch counts from alphas_dataset curated folders
curated_counts = {}
if os.path.exists(ad_dir):
    for ds_folder in os.listdir(ad_dir):
        path = os.path.join(ad_dir, ds_folder, 'fields.json')
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                curated_counts[ds_folder.lower().replace('_', '')] = len(data)
            except Exception as e:
                pass

# 3. Fetch counts from downloaded field details
downloaded_counts = {}
if os.path.exists(selected_fields_dir):
    for fn in os.listdir(selected_fields_dir):
        if fn.endswith('_fields.json'):
            ds_id = fn.replace('_fields.json', '').lower().replace('_', '')
            path = os.path.join(selected_fields_dir, fn)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                downloaded_counts[ds_id] = len(data)
            except Exception as e:
                pass

# Compile results table
results = []
for ds in theme_datasets:
    ds_id = ds['id']
    key = ds_id.lower().replace('_', '')
    
    db_val = db_counts.get(key, 0)
    curated_val = curated_counts.get(key, 0)
    downloaded_val = downloaded_counts.get(key, 0)
    
    results.append({
        'id': ds_id,
        'name': ds['name'],
        'category': ds['category'],
        'db_whitelist': db_val,
        'curated_whitelist': curated_val,
        'downloaded_all': downloaded_val
    })

print(json.dumps(results, indent=2))

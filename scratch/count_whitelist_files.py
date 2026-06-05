import os
import json

ad_dir = r"c:\Users\Admin\Documents\VIBE_YT\wq\alphas_dataset"
theme_json_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\theme_Dataset.json"

with open(theme_json_path, 'r', encoding='utf-8') as f:
    theme_datasets = json.load(f)

theme_ids = [d['id'] for d in theme_datasets]

print("Scanning alphas_dataset folders:")
for root, dirs, files in os.walk(ad_dir):
    for file in files:
        if file in ['fields.json', 'whitelist.json', 'variables.json', 'variables_all.json']:
            path = os.path.join(root, file)
            # Find which dataset folder it is in
            rel = os.path.relpath(path, ad_dir)
            parts = rel.split(os.sep)
            dataset_name = parts[0]
            
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                count = len(data) if isinstance(data, list) else (len(data.get('results', [])) if isinstance(data, dict) and 'results' in data else 0)
                print(f"  {dataset_name}/{file}: {count} fields")
            except Exception as e:
                print(f"  Error reading {rel}: {e}")

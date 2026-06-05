import json

path = r"c:\Users\Admin\Documents\VIBE_YT\wq\scratch\analyst_fields_sai\available_datasets.json"
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for ds in data:
    if ds.get('id') == 'analyst16':
        print(json.dumps(ds, indent=2))
        break

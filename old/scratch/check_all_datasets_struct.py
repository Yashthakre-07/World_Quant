import json

all_datasets_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\documentation\dataset\all_datasets.json"

with open(all_datasets_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Type of data:", type(data))
if isinstance(data, dict):
    print("Keys of dictionary:", list(data.keys()))
    for k, v in list(data.items())[:2]:
        print(f"Key: {k}, Type of value: {type(v)}")
        if isinstance(v, list) and len(v) > 0:
            print("First item in list:", list(v[0].keys()) if isinstance(v[0], dict) else type(v[0]))
        elif isinstance(v, dict):
            print("Subkeys:", list(v.keys())[:5])
elif isinstance(data, list):
    print("Length of list:", len(data))
    if len(data) > 0:
        print("First item in list keys:", list(data[0].keys()) if isinstance(data[0], dict) else type(data[0]))

import json
with open("both_servers_report.json", "r") as f:
    data = json.load(f)

print("Keys in JSON:", data.keys() if isinstance(data, dict) else "List")
if isinstance(data, dict):
    for k, v in data.items():
        print(f"Key: {k}, Type: {type(v)}, Length: {len(v) if hasattr(v, '__len__') else 'N/A'}")
elif isinstance(data, list):
    print("List size:", len(data))
    if len(data) > 0:
        print("Sample item keys:", data[0].keys())

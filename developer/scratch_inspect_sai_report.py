import json
with open("sai_server_report.json", "r") as f:
    data = json.load(f)

print("Keys inside sai_server_report.json:", data.keys() if isinstance(data, dict) else "List")
if isinstance(data, dict):
    for k, v in data.items():
        print(f"Key: {k}, Type: {type(v)}, Length: {len(v) if hasattr(v, '__len__') else 'N/A'}")

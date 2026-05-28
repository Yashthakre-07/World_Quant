import json
with open("both_servers_report.json", "r") as f:
    data = json.load(f)

for server, sdata in data.items():
    print(f"\nServer: {server}")
    print("Keys inside server:", sdata.keys())
    for k, v in sdata.items():
        print(f"  Key: {k}, Type: {type(v)}, Length: {len(v) if hasattr(v, '__len__') else 'N/A'}")

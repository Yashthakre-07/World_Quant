import json
with open("both_servers_report.json", "r") as f:
    data = json.load(f)

for server, sdata in data.items():
    print(f"\nServer: {server}")
    alphas = sdata.get('alphas', {})
    print("Alphas keys:", alphas.keys())
    for k, v in alphas.items():
        print(f"  Key: {k}, Type: {type(v)}, Length: {len(v) if hasattr(v, '__len__') else 'N/A'}")
        if isinstance(v, list) and len(v) > 0:
            print("  Sample element keys:", v[0].keys())

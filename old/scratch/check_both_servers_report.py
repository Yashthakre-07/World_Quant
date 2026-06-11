import json

with open("developer/both_servers_report.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for server_name, server_data in data.items():
    print(f"\nServer: {server_name}")
    stats = server_data.get('stats', {})
    for k, v in stats.items():
        if isinstance(v, list):
            print(f"  List Key in stats: {k}, length: {len(v)}")
            if len(v) > 0:
                print(f"    First element: {v[0]}")
        else:
            print(f"  Key in stats: {k}, value: {v}")

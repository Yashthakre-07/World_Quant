import json
with open("sai_server_report.json", "r") as f:
    data = json.load(f)

alphas = data.get('alphas', {})
print("Alphas keys:", alphas.keys())
for k, v in alphas.items():
    print(f"  Key: {k}, Type: {type(v)}, Length: {len(v) if hasattr(v, '__len__') else 'N/A'}")

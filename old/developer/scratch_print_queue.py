import json

with open("sai_server_report.json", "r") as f:
    report = json.load(f)

alphas = report.get("status", {}).get("alphas", [])
print(f"=== REMOTE QUEUE ACTIVE STATUS (Total: {len(alphas)}) ===")
for i, a in enumerate(alphas):
    print(f"{i+1}. [{a.get('status')}] {a.get('family')}")
    print(f"   Formula: {a.get('formula')[:100]}...")

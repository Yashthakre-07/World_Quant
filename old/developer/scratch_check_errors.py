import json

with open("both_servers_report.json", "r") as f:
    report = json.load(f)

for name, server_data in report.items():
    print(f"\n==========================================")
    print(f"ERRORS ON SERVER: {name}")
    print(f"==========================================")
    
    status_data = server_data.get("status", {})
    alphas_in_pipeline = status_data.get("alphas", [])
    
    error_alphas = [a for a in alphas_in_pipeline if a.get("status") == "ERROR"]
    print(f"Total errors: {len(error_alphas)}")
    for idx, a in enumerate(error_alphas):
        print(f"  [{idx+1}] Formula: {a.get('formula')[:100]}...")
        print(f"      Error: {a.get('error_message')}")

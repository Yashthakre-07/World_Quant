import json

with open("sai_server_report.json", "r") as f:
    report = json.load(f)

alphas = report.get("status", {}).get("alphas", [])
failed_count = 0

print("=== FAILED ALPHAS ANALYSIS ===")
for i, a in enumerate(alphas):
    status = a.get("status")
    err = a.get("error_message")
    if err or status in ["ERROR", "HARD_REJECT", "SOFT_FAIL"]:
        failed_count += 1
        print(f"\n[{failed_count}] Family: {a.get('family')}")
        print(f"    Formula: {a.get('formula')}")
        print(f"    Status: {status}")
        print(f"    Error: {err}")
print(f"\nTotal failed/error alphas found: {failed_count}")

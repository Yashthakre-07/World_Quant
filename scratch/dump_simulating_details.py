import requests
import json
import urllib3
urllib3.disable_warnings()

url = "https://world-quant.onrender.com/api/status"
r = requests.get(url, verify=False)
data = r.json()
alphas = data.get("alphas", [])

simulating = [a for a in alphas if a.get("status") == "SIMULATING"]
errors = [a for a in alphas if a.get("status") == "ERROR"]
completed = [a for a in alphas if a.get("status") not in ("SIMULATING", "ERROR")]

print(f"Total alphas: {len(alphas)}")
print(f"Simulating: {len(simulating)}")
print(f"Errors: {len(errors)}")
print(f"Other statuses: {len(completed)}")

print("\n--- Top 10 Simulating Alphas ---")
for idx, a in enumerate(simulating[:10]):
    print(f"[{idx+1}] Slot ID: {a.get('slot_id')} | Progress: {a.get('progress')}% | Created: {a.get('created_at')} | Formula: {a.get('formula')[:100]}...")

print("\n--- Top 10 Errors ---")
for idx, a in enumerate(errors[:10]):
    print(f"[{idx+1}] Slot ID: {a.get('slot_id')} | Created: {a.get('created_at')} | Error: {a.get('error_message')} | Formula: {a.get('formula')[:100]}...")

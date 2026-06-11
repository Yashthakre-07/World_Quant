import requests
import json
import urllib3
urllib3.disable_warnings()

url = "https://world-quant.onrender.com/api/status"
r = requests.get(url, verify=False)
data = r.json()
alphas = data.get("alphas", [])

print(f"Total alphas: {len(alphas)}")
print("\n--- Detailed Queue Alphas ---")
for idx, a in enumerate(alphas):
    print(f"[{idx+1}] Slot ID: {a.get('slot_id')} | Status: {a.get('status')} | Error: {a.get('error_message')} | Formula: {a.get('formula')}")

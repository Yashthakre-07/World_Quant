import requests
import json
import urllib3
urllib3.disable_warnings()

url = "https://world-quant.onrender.com/api/status"
r = requests.get(url, timeout=30, verify=False)
if r.status_code == 200:
    data = r.json()
    alphas = data.get("alphas", [])
    print(f"Total alphas in queue: {len(alphas)}")
    
    target_pattern = "group_zscore(rank("
    count_matched = 0
    
    for a in alphas:
        formula = a.get("formula", "")
        if target_pattern in formula.replace(" ", ""):
            count_matched += 1
            print(f"\n--- Alpha #{count_matched} ---")
            print(f"Formula: {formula}")
            print(f"Status: {a.get('status')}")
            print(f"Progress: {a.get('progress')}%")
            print(f"Error Message: {a.get('error_message')}")
            print(f"Sharpe: {a.get('sharpe')} | Fitness: {a.get('fitness')}")
else:
    print(f"Failed to fetch status: {r.status_code}")

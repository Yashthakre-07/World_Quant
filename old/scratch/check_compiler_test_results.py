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
    
    # Print the compiler test cases (indices 0 to 7)
    for idx in range(min(8, len(alphas))):
        a = alphas[idx]
        print(f"\n--- Test #{idx+1} ---")
        print(f"Formula: {a.get('formula')}")
        print(f"Status: {a.get('status')}")
        print(f"Progress: {a.get('progress')}%")
        print(f"Error Message: {a.get('error_message')}")
        print(f"Sharpe: {a.get('sharpe')} | Fitness: {a.get('fitness')}")
else:
    print(f"Failed to fetch status: {r.status_code}")

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://world-quant.onrender.com/api/status"
headers = {
    "Authorization": "Bearer yashthakrepro",
    "Content-Type": "application/json"
}

try:
    r = requests.get(url, headers=headers, verify=False, timeout=30)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Pipeline status: {data.get('status')}")
        alphas = data.get("alphas", [])
        print(f"Alphas found: {len(alphas)}")
        for idx, a in enumerate(alphas):
            print(f"\n[{idx+1}] Slot: {a.get('slot_id')}")
            print(f"    Family: {a.get('family')}")
            print(f"    Status: {a.get('status')}")
            print(f"    Progress: {a.get('progress')}%")
            print(f"    Sharpe: {a.get('sharpe')}")
            print(f"    Fitness: {a.get('fitness')}")
            print(f"    Turnover: {a.get('turnover')}")
            print(f"    Error: {a.get('error_message')}")
            print(f"    Formula: {a.get('formula')}")
    else:
        print(f"Error: {r.text}")
except Exception as e:
    print(f"Request failed: {e}")

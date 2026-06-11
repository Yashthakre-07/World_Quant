import requests
import urllib3
urllib3.disable_warnings()

url = "https://world-quant.onrender.com/api/alphas"
headers = {"Authorization": "Bearer yashthakreop"}

try:
    r = requests.get(url, headers=headers, timeout=30, verify=False)
    if r.status_code == 200:
        data = r.json()
        alphas = data.get("alphas", [])
        submitted = [a for a in alphas if a.get("status") == "SUBMITTED"]
        
        print("=" * 70)
        print(f"SUBMITTED ALPHAS ON SAI'S ACCOUNT (Total: {len(submitted)}):")
        print("=" * 70)
        
        for idx, a in enumerate(submitted, 1):
            print(f"{idx:02d}. Sharpe: {a.get('sharpe')} | Fitness: {a.get('fitness')} | Turnover: {a.get('turnover')}%")
            print(f"    Formula: {a.get('formula')}")
            print("-" * 70)
    else:
        print(f"Failed to fetch alphas: {r.status_code} - {r.text[:300]}")
except Exception as e:
    print(f"Connection failed: {e}")

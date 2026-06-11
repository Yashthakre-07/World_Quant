import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

r = requests.get('https://world-quant.onrender.com/api/status', verify=False)
if r.status_code == 200:
    data = r.json()
    alphas = data.get("alphas", [])
    print(f"Total Alphas in status: {len(alphas)}")
    for idx, a in enumerate(alphas[:10]):
        print(f"  [{idx}] Formula: {a['formula'][:80]}... | Status: {a['status']}")
else:
    print(f"Failed to fetch status: {r.status_code}")

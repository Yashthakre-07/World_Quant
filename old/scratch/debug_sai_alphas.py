import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://world-quant.onrender.com/api/status"
r = requests.get(url, verify=False)
if r.status_code == 200:
    data = r.json()
    alphas = data.get("alphas", [])
    print("ALPHAS #61 to #71:")
    for idx in range(60, min(75, len(alphas))):
        a = alphas[idx]
        print(f"Index {idx} (Alpha #{idx+1}):")
        print(f"  Formula: {a.get('formula')}")
        print(f"  Status: {a.get('status')}")
        print(f"  Error Message: {a.get('error_message')}")
        print("-" * 50)
else:
    print(f"Failed to fetch status: {r.status_code}")

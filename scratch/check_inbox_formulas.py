import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://world-quant.onrender.com/api/status"
try:
    r = requests.get(url, timeout=30, verify=False)
    if r.status_code == 200:
        data = r.json()
        alphas = data.get("alphas", [])
        print(f"Total alphas in queue: {len(alphas)}")
        for idx, a in enumerate(alphas):
            print(f"Index: {idx} | ID: {a.get('id')} | Status: {a.get('status')}")
            print(f"  Formula: {a.get('formula')}")
            print(f"  Error: {a.get('error_message')}")
            print("-" * 50)
    else:
        print(f"Error: status code {r.status_code}")
except Exception as e:
    print(f"Failed: {e}")

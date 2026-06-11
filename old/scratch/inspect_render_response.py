import requests
import json
import urllib3
urllib3.disable_warnings()

url = "https://world-quant.onrender.com/api/alphas"
headers = {"Authorization": "Bearer yashthakreop"}

try:
    r = requests.get(url, headers=headers, timeout=30, verify=False)
    if r.status_code == 200:
        data = r.json()
        print("Response type:", type(data))
        if isinstance(data, dict):
            print("Response keys:", list(data.keys()))
            alphas = data.get("alphas", [])
            print(f"Total alphas: {len(alphas)}")
            if alphas:
                print("\nSample alpha keys:", list(alphas[0].keys()))
                print("\nSample alpha JSON:")
                print(json.dumps(alphas[0], indent=2))
        else:
            print("Sample raw list response:")
            print(json.dumps(data[:3], indent=2))
    else:
        print(f"Status: {r.status_code}, Text: {r.text}")
except Exception as e:
    print("Error:", e)

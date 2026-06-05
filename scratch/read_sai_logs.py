import requests
import json
import urllib3
urllib3.disable_warnings()

url = "https://world-quant.onrender.com/api/status"
r = requests.get(url, timeout=30, verify=False)
if r.status_code == 200:
    data = r.json()
    logs = data.get("logs", [])
    print("Sai's Server Logs:")
    for log in logs[-30:]:
        print(log)
else:
    print(f"Failed to fetch status: {r.status_code}")

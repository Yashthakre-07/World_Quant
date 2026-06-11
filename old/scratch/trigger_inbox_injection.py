import requests
import json
import urllib3
urllib3.disable_warnings()

url = "https://world-quant.onrender.com/api/inject-inbox"
headers = {
    "Authorization": "Bearer yashthakreop",
    "Content-Type": "application/json"
}
payload = {
    "all": True
}

try:
    r = requests.post(url, json=payload, headers=headers, timeout=30, verify=False)
    print(f"Injection Status Code: {r.status_code}")
    print(f"Response: {r.json()}")
except Exception as e:
    print(f"Error triggering injection: {e}")

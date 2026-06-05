import requests
import urllib3
urllib3.disable_warnings()

url = "https://world-quant.onrender.com/api/status"
r = requests.get(url, verify=False)
data = r.json()
logs = data.get("logs", [])
print(f"Total log count: {len(logs)}")
print("\n--- Last 15 Server Logs ---")
for idx, log in enumerate(logs[-15:]):
    print(f"[{idx+1}] {log}")

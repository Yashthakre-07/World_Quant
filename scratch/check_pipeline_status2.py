import requests
import urllib3
urllib3.disable_warnings()

SERVERS = {
    "world-quant (Sai Profile)": "https://world-quant.onrender.com",
    "world-quant-1 (Yash Profile)": "https://world-quant-1.onrender.com"
}

for name, base in SERVERS.items():
    print(f"\n--- {name} ---")
    try:
        r = requests.get(f"{base}/api/queue-status", timeout=10, verify=False)
        if r.status_code == 200:
            data = r.json()
            print(data)
        else:
            print(f"Error: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        print(f"Request failed: {e}")

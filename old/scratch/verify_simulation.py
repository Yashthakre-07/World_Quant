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
        print(f"Status Data: {r.json()}")
    except Exception as e:
        print(f"Error: {e}")

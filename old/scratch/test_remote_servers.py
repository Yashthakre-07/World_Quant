import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SERVERS = {
    "world-quant (Sai Profile)": "https://world-quant.onrender.com/api/session",
    "world-quant-1 (Yash Profile)": "https://world-quant-1.onrender.com/api/session"
}

for name, url in SERVERS.items():
    print(f"Checking server: {name} ({url}) ...")
    try:
        r = requests.get(url, timeout=30, verify=False)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            print(f"Response: {r.json()}")
        else:
            print(f"Response Text: {r.text[:300]}")
    except Exception as e:
        print(f"Connection failed: {e}")
    print("-" * 50)

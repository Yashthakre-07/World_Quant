import requests
import urllib3
urllib3.disable_warnings()

SERVERS = {
    "world-quant (Sai Profile)": {
        "base": "https://world-quant.onrender.com",
        "token": "yashthakreop",
    },
    "world-quant-1 (Yash Profile)": {
        "base": "https://world-quant-1.onrender.com",
        "token": "yashthakreop1",
    }
}

for name, info in SERVERS.items():
    print(f"\n--- {name} ---")
    headers = {
        "Authorization": f"Bearer {info['token']}",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.post(f"{info['base']}/api/reauthenticate", headers=headers, timeout=15, verify=False)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(r.json())
        else:
            print(r.text[:200])
    except Exception as e:
        print(f"Error: {e}")

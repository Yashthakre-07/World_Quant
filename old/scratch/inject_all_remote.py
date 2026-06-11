import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URLS = {
    "world-quant (Sai Profile)": {
        "url": "https://world-quant.onrender.com/api/inject-inbox",
        "token": "yashthakreop"
    },
    "world-quant-1 (Yash Profile)": {
        "url": "https://world-quant-1.onrender.com/api/inject-inbox",
        "token": "yashthakreop1"
    }
}

for name, info in URLS.items():
    print("=" * 70)
    print(f"INJECTING ALL PENDING ALPHAS ON: {name}")
    print("=" * 70)
    
    headers = {
        "Authorization": f"Bearer {info['token']}",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.post(info["url"], headers=headers, json={"all": True}, timeout=40, verify=False)
        if r.status_code == 200:
            res_data = r.json()
            print(f"[SUCCESS] Inbox successfully injected into queue on {name}.")
            print(f"Server Response: {res_data}")
        else:
            print(f"[FAILED] Server {name} returned status code {r.status_code}")
            print(f"Server Response: {r.text[:300]}")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
    print("\n" + "=" * 70 + "\n")

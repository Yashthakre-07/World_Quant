import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URLS = {
    "world-quant (Sai Profile)": {
        "url": "https://world-quant.onrender.com/api/start-pipeline",
        "token": "yashthakreop"
    },
    "world-quant-1 (Yash Profile)": {
        "url": "https://world-quant-1.onrender.com/api/start-pipeline",
        "token": "yashthakreop1"
    }
}

for name, info in URLS.items():
    print(f"FORCING PIPELINE START ON: {name}")
    headers = {
        "Authorization": f"Bearer {info['token']}",
        "Content-Type": "application/json"
    }
    try:
        r = requests.post(info["url"], headers=headers, json={}, timeout=40, verify=False)
        if r.status_code == 200:
            print(f"[SUCCESS] Pipeline started/resumed on {name}.")
            print(f"Response: {r.json()}")
        else:
            print(f"[FAILED] Status code {r.status_code}: {r.text[:300]}")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

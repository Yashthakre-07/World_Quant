"""
Deep dive into pipeline errors — fetch all alpha details from run_pipeline DB or logs.
"""
import requests
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SERVERS = {
    "world-quant (Sai Profile)": {
        "status_url": "https://world-quant.onrender.com/api/status",
        "logs_url":   "https://world-quant.onrender.com/api/logs",
        "token": "yashthakreop"
    },
    "world-quant-1 (Yash Profile)": {
        "status_url": "https://world-quant-1.onrender.com/api/status",
        "logs_url":   "https://world-quant-1.onrender.com/api/logs",
        "token": "yashthakreop1"
    }
}

for name, info in SERVERS.items():
    print("=" * 70)
    print(f"SERVER: {name}")
    print("=" * 70)
    headers = {
        "Authorization": f"Bearer {info['token']}",
        "Content-Type": "application/json"
    }

    # Try logs endpoint first
    try:
        lr = requests.get(info["logs_url"], headers=headers, timeout=30, verify=False)
        print(f"[LOGS] Status: {lr.status_code}")
        if lr.status_code == 200:
            logs = lr.text
            # Print last 3000 chars of logs to capture recent errors
            print("Last 3000 chars of logs:")
            print(logs[-3000:])
        else:
            print(f"[LOGS] Response: {lr.text[:300]}")
    except Exception as e:
        print(f"[LOGS ERROR] {e}")

    # Try status with full alpha details
    try:
        sr = requests.get(info["status_url"], headers=headers, timeout=30, verify=False)
        if sr.status_code == 200:
            data = sr.json()
            alphas = data.get("alphas", [])
            errors = [a for a in alphas if a.get("status") in ("ERROR", "HARD_REJECT")]
            print(f"\nFull data keys for first error alpha: {list(errors[0].keys()) if errors else 'None'}")
            if errors:
                print(f"\nFull detail of first error alpha:")
                print(json.dumps(errors[0], indent=2))
                print(f"\nFull detail of second error alpha:")
                print(json.dumps(errors[1], indent=2) if len(errors) > 1 else "N/A")
    except Exception as e:
        print(f"[STATUS ERROR] {e}")
    print()

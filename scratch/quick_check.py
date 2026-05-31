import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests, json
import urllib3
urllib3.disable_warnings()

SERVERS = [
    {"name": "SAI", "base": "https://world-quant.onrender.com", "token": "yashthakreop"},
    {"name": "YASH", "base": "https://world-quant-1.onrender.com", "token": "yashthakreop1"},
]

for s in SERVERS:
    h = {"Authorization": f"Bearer {s['token']}", "Content-Type": "application/json"}
    print(f"\n=== {s['name']} ({s['base']}) ===")
    
    # Status
    try:
        r = requests.get(f"{s['base']}/api/status", headers=h, timeout=25, verify=False)
        print(f"  /api/status  HTTP {r.status_code}")
        if r.status_code == 200:
            d = r.json()
            print(f"    -> {json.dumps(d, indent=6)[:600]}")
    except Exception as e:
        print(f"  /api/status  ERROR: {e}")

    # Queue
    try:
        r = requests.get(f"{s['base']}/api/queue", headers=h, timeout=25, verify=False)
        print(f"  /api/queue   HTTP {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                print(f"    -> {len(data)} items in queue")
                # Count statuses
                statuses = {}
                errors = []
                for item in data:
                    st = item.get("status", item.get("state", "unknown"))
                    statuses[st] = statuses.get(st, 0) + 1
                    err = item.get("error", item.get("errorMessage", item.get("err", "")))
                    if err:
                        errors.append({"formula": item.get("formula","")[:80], "error": str(err)[:200]})
                print(f"    Status breakdown: {statuses}")
                if errors:
                    print(f"    ERRORS ({len(errors)}):")
                    for e in errors[:5]:
                        print(f"      formula: {e['formula']}")
                        print(f"      error  : {e['error']}")
            elif isinstance(data, dict):
                print(f"    -> {json.dumps(data, indent=6)[:600]}")
        else:
            print(f"    Body: {r.text[:300]}")
    except Exception as e:
        print(f"  /api/queue   ERROR: {e}")

    # Inbox
    try:
        r = requests.get(f"{s['base']}/api/inbox", headers=h, timeout=25, verify=False)
        print(f"  /api/inbox   HTTP {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                print(f"    -> {len(data)} items in inbox")
                statuses = {}
                errors = []
                for item in data:
                    st = item.get("status", item.get("state", "pending"))
                    statuses[st] = statuses.get(st, 0) + 1
                    err = item.get("error", item.get("errorMessage", item.get("err", "")))
                    if err:
                        errors.append({"formula": item.get("formula","")[:80], "error": str(err)[:200]})
                print(f"    Status breakdown: {statuses}")
                if errors:
                    print(f"    ERRORS ({len(errors)}):")
                    for e in errors[:5]:
                        print(f"      formula: {e['formula']}")
                        print(f"      error  : {e['error']}")
            elif isinstance(data, dict):
                print(f"    -> {json.dumps(data, indent=6)[:600]}")
        else:
            print(f"    Body: {r.text[:300]}")
    except Exception as e:
        print(f"  /api/inbox   ERROR: {e}")

    # Errors endpoint
    try:
        r = requests.get(f"{s['base']}/api/errors", headers=h, timeout=25, verify=False)
        print(f"  /api/errors  HTTP {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and data:
                print(f"    -> {len(data)} errors logged")
                for e in data[:5]:
                    print(f"      {str(e)[:250]}")
            elif isinstance(data, dict):
                print(f"    -> {json.dumps(data)[:400]}")
            else:
                print(f"    -> {data}")
        else:
            print(f"    Body: {r.text[:200]}")
    except Exception as e:
        print(f"  /api/errors  ERROR: {e}")

    # Submitted alphas count
    try:
        r = requests.get(f"{s['base']}/api/submitted-alphas", headers=h, timeout=25, verify=False)
        print(f"  /api/submitted-alphas  HTTP {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                print(f"    -> {len(data)} submitted alphas")
            else:
                print(f"    -> {json.dumps(data)[:300]}")
        else:
            print(f"    Body: {r.text[:200]}")
    except Exception as e:
        print(f"  /api/submitted-alphas  ERROR: {e}")

print("\n=== DONE ===")

# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
check_queue_status_now.py
=========================
Deep diagnostic: check queue, inbox, errors, and simulation status on both servers.
"""
import requests
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SERVERS = {
    "SAI (world-quant.onrender.com)": {
        "base": "https://world-quant.onrender.com",
        "token": "yashthakreop"
    },
    "YASH (world-quant-1.onrender.com)": {
        "base": "https://world-quant-1.onrender.com",
        "token": "yashthakreop1"
    }
}

ENDPOINTS = [
    "/api/status",
    "/api/queue",
    "/api/inbox",
    "/api/submitted-alphas",
    "/api/errors",
    "/api/vault",
]

def check_server(name, info):
    base = info["base"]
    token = info["token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print(f"\n{'='*70}")
    print(f"SERVER: {name}")
    print(f"{'='*70}")
    
    for endpoint in ENDPOINTS:
        url = f"{base}{endpoint}"
        try:
            r = requests.get(url, headers=headers, timeout=20, verify=False)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list):
                    print(f"\n  [{endpoint}] -> {len(data)} items")
                    # Show first 3 items
                    for i, item in enumerate(data[:3]):
                        if isinstance(item, dict):
                            formula = item.get("formula", item.get("regular", "N/A"))[:80]
                            family = item.get("family", item.get("name", "N/A"))
                            status = item.get("status", item.get("state", "N/A"))
                            error = item.get("error", item.get("errorMessage", ""))
                            print(f"    [{i+1}] family={family}")
                            print(f"         status={status}")
                            if error:
                                print(f"         ERROR: {str(error)[:200]}")
                            print(f"         formula={formula}...")
                        else:
                            print(f"    [{i+1}] {str(item)[:100]}")
                    if len(data) > 3:
                        print(f"    ... and {len(data)-3} more items")
                elif isinstance(data, dict):
                    print(f"\n  [{endpoint}] ->")
                    # Print key stats
                    for k, v in data.items():
                        if isinstance(v, (str, int, float, bool)):
                            print(f"    {k}: {v}")
                        elif isinstance(v, list):
                            print(f"    {k}: [{len(v)} items]")
                        elif isinstance(v, dict):
                            print(f"    {k}: {{...}}")
                    # Check for errors inside status
                    if "errors" in data:
                        errs = data["errors"]
                        if errs:
                            print(f"\n  ⚠️  ERRORS FOUND ({len(errs)}):")
                            for e in errs[:5]:
                                print(f"    - {str(e)[:200]}")
                else:
                    print(f"\n  [{endpoint}] -> {str(data)[:200]}")
            else:
                print(f"\n  [{endpoint}] -> HTTP {r.status_code}: {r.text[:150]}")
        except Exception as e:
            print(f"\n  [{endpoint}] -> CONNECTION ERROR: {e}")

    # Extra: Check queue alpha count in detail
    print(f"\n  --- QUEUE DETAIL ---")
    try:
        r = requests.get(f"{base}/api/queue", headers=headers, timeout=20, verify=False)
        if r.status_code == 200:
            queue = r.json()
            if isinstance(queue, list):
                statuses = {}
                errors_found = []
                for item in queue:
                    s = item.get("status", item.get("state", "unknown"))
                    statuses[s] = statuses.get(s, 0) + 1
                    err = item.get("error", item.get("errorMessage", ""))
                    if err:
                        errors_found.append({
                            "formula": item.get("formula", "")[:100],
                            "error": str(err)[:200]
                        })
                print(f"  Status breakdown: {json.dumps(statuses, indent=4)}")
                if errors_found:
                    print(f"\n  ❌ ITEMS WITH ERRORS ({len(errors_found)}):")
                    for e in errors_found[:5]:
                        print(f"    Formula: {e['formula']}...")
                        print(f"    Error  : {e['error']}")
                        print()
    except Exception as e:
        print(f"  Queue detail error: {e}")

    # Extra: Check inbox in detail
    print(f"\n  --- INBOX DETAIL ---")
    try:
        r = requests.get(f"{base}/api/inbox", headers=headers, timeout=20, verify=False)
        if r.status_code == 200:
            inbox = r.json()
            if isinstance(inbox, list):
                statuses = {}
                errors_found = []
                for item in inbox:
                    s = item.get("status", item.get("state", "pending"))
                    statuses[s] = statuses.get(s, 0) + 1
                    err = item.get("error", item.get("errorMessage", ""))
                    if err:
                        errors_found.append({
                            "formula": item.get("formula", "")[:100],
                            "error": str(err)[:200]
                        })
                print(f"  Inbox status breakdown: {json.dumps(statuses, indent=4)}")
                if errors_found:
                    print(f"\n  ❌ INBOX ITEMS WITH ERRORS ({len(errors_found)}):")
                    for e in errors_found[:5]:
                        print(f"    Formula: {e['formula']}...")
                        print(f"    Error  : {e['error']}")
    except Exception as e:
        print(f"  Inbox detail error: {e}")

for name, info in SERVERS.items():
    check_server(name, info)

print(f"\n{'='*70}")
print("DIAGNOSTIC COMPLETE")
print(f"{'='*70}")

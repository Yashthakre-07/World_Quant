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
    
    # Get full status with alphas and logs
    try:
        r = requests.get(f"{s['base']}/api/status", headers=h, timeout=45, verify=False)
        print(f"  /api/status  HTTP {r.status_code}")
        if r.status_code == 200:
            d = r.json()
            
            # Overall status
            print(f"  Pipeline Status: {d.get('status', 'N/A')}")
            print(f"  Current Alpha:   {d.get('currentAlpha', d.get('current_alpha', 'N/A'))}")
            print(f"  Total Alphas:    {d.get('totalAlphas', d.get('total_alphas', len(d.get('alphas', []))))}")
            print(f"  Progress:        {d.get('progress', 'N/A')}")
            
            # Check alphas list
            alphas = d.get('alphas', [])
            print(f"\n  --- ALPHA RESULTS ({len(alphas)} total) ---")
            
            status_counts = {}
            errors_found = []
            
            for item in alphas:
                st = item.get("status", item.get("state", "unknown"))
                status_counts[st] = status_counts.get(st, 0) + 1
                
                err = item.get("error", item.get("errorMessage", item.get("err", "")))
                if err or st in ("error", "failed", "ERROR", "FAILED"):
                    errors_found.append({
                        "name": item.get("name", item.get("id", "??")),
                        "formula": item.get("formula", item.get("regular", ""))[:100],
                        "status": st,
                        "error": str(err)[:300] if err else "No error message"
                    })
                    
            print(f"  Status Breakdown: {json.dumps(status_counts, indent=4)}")
            
            if errors_found:
                print(f"\n  FAILED/ERROR ALPHAS ({len(errors_found)}):")
                for e in errors_found[:10]:
                    print(f"    Name   : {e['name']}")
                    print(f"    Status : {e['status']}")
                    print(f"    Formula: {e['formula']}...")
                    print(f"    Error  : {e['error']}")
                    print()
            else:
                print("\n  No error alphas detected.")
            
            # Show sample of passing/completed alphas
            completed = [a for a in alphas if a.get("status", a.get("state","")) in ("completed", "COMPLETED", "done", "DONE", "success", "SUCCESS")]
            if completed:
                print(f"\n  SAMPLE COMPLETED ALPHAS (first 3):")
                for a in completed[:3]:
                    print(f"    Name     : {a.get('name', a.get('id', '??'))}")
                    print(f"    Sharpe   : {a.get('sharpe', a.get('is', a.get('fitness', 'N/A')))}")
                    print(f"    Fitness  : {a.get('fitness', a.get('metrics', {}).get('fitness', 'N/A')) if isinstance(a.get('metrics'), dict) else a.get('fitness','N/A')}")
                    print()

            # Show recent logs
            logs = d.get('logs', [])
            if logs:
                print(f"\n  RECENT LOGS (last 10):")
                for log in logs[-10:]:
                    print(f"    {str(log)[:200]}")
            
    except Exception as e:
        print(f"  ERROR: {e}")

    # Try queue-alpha endpoint (POST to see what's there via GET if supported)
    print(f"\n  --- Checking queue-alpha-list or similar ---")
    for endpoint in ["/api/queue-alpha", "/api/alpha-queue", "/api/alphas", "/api/review"]:
        try:
            r = requests.get(f"{s['base']}{endpoint}", headers=h, timeout=15, verify=False)
            if r.status_code == 200:
                data = r.json()
                print(f"    {endpoint}: {len(data) if isinstance(data, list) else data}")
            else:
                print(f"    {endpoint}: HTTP {r.status_code}")
        except Exception as e:
            print(f"    {endpoint}: ERROR {e}")

print("\n=== DONE ===")

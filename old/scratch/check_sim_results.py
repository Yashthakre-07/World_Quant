import urllib.request
import json

tokens = {
    "GROUP-A (yashthakreop)": "yashthakreop",
    "GROUP-B (yashthakrepro)": "yashthakrepro"
}

for group_name, token in tokens.items():
    print(f"\n==========================================")
    print(f"  STATUS FOR {group_name}")
    print(f"==========================================")
    
    url = "http://localhost:8000/api/status"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })

    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
            alphas = data.get("alphas", [])
            print(f"Total alphas: {len(alphas)}")
            
            # Group by slot
            slots = {}
            for a in alphas:
                sid = a.get("slot_id")
                if sid not in slots:
                    slots[sid] = []
                slots[sid].append(a)
                
            for sid in sorted(slots.keys(), key=lambda x: x if x is not None else 0):
                print(f"\nSlot {sid}:")
                for a in slots[sid]:
                    print(f"  - Status: {a.get('status')} | Sharpe: {a.get('sharpe')} | Fitness: {a.get('fitness')} | Turnover: {a.get('turnover')}")
                    print(f"    Formula: {a.get('formula')}")
    except Exception as e:
        print("Error querying status:", e)


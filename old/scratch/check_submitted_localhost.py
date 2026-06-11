import urllib.request
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    tokens = [("yashthakreop", "GROUP A"), ("yashthakrepro", "GROUP B")]
    
    print("==========================================")
    print("SUBMITTED ALPHAS ON LOCALHOST CURRENTLY")
    print("==========================================\n")
    
    for token, group_name in tokens:
        url = "http://localhost:8000/api/status"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode("utf-8"))
                alphas = data.get("alphas", [])
                
                submitted = [a for a in alphas if a.get("status") == "SUBMITTED"]
                print(f"{group_name}: Found {len(submitted)} SUBMITTED alphas.")
                for a in submitted:
                    print(f"  Slot: {a.get('slot_id')} | Sharpe: {a.get('sharpe')} | Fit: {a.get('fitness')} | Turn: {a.get('turnover')}%")
                    print(f"  Formula: {a.get('formula')}")
                    print("-" * 40)
        except Exception as e:
            print(f"Error checking {group_name}: {e}")

if __name__ == "__main__":
    main()

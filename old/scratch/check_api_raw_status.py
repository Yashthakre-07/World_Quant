import urllib.request
import json

def main():
    base = "http://localhost:8000"
    for name, token in [("Group A", "yashthakreop"), ("Group B", "yashthakrepro")]:
        print(f"\n=== {name} ===")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        try:
            req = urllib.request.Request(base + "/api/status", headers=headers)
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
                print(f"Status Keys: {list(data.keys())}")
                print(f"Total Alphas: {len(data.get('alphas', []))}")
                print("First 3 Alphas:")
                for a in data.get('alphas', [])[:3]:
                    print(f"  Slot: {a.get('slot_id')} | Status: {a.get('status')} | Sharpe: {a.get('sharpe')} | Formula: {a.get('formula')[:80]}...")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    main()

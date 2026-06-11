import urllib.request
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    tokens = [("yashthakreop", "GROUP A"), ("yashthakrepro", "GROUP B")]
    
    for token, name in tokens:
        print(f"\n===== {name} =====")
        for endpoint in ["/api/queue", "/api/status", "/api/inbox"]:
            url = f"http://localhost:8000{endpoint}"
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
            try:
                with urllib.request.urlopen(req, timeout=5) as r:
                    res = json.loads(r.read().decode('utf-8'))
                    if isinstance(res, list):
                        print(f"  {endpoint}: {len(res)} items")
                        for i, item in enumerate(res[:3]):
                            print(f"    - {item.get('formula')[:60]}... (status: {item.get('status')})")
                    elif isinstance(res, dict):
                        print(f"  {endpoint}: dict with keys {list(res.keys())}")
                        if "alphas" in res:
                            alphas = res["alphas"]
                            print(f"    - alphas: {len(alphas)} items")
                            for idx, a in enumerate(alphas[:5]):
                                print(f"      - {a.get('formula')[:60]}... (status: {a.get('status') or a.get('state')})")
            except Exception as e:
                print(f"  {endpoint} Error: {e}")

if __name__ == "__main__":
    main()

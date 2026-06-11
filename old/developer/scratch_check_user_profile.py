import json
from src.auth import WQSession

def main():
    session = WQSession()
    
    endpoints = [
        "https://api.worldquantbrain.com/users/self",
        "https://api.worldquantbrain.com/users/self/subscriptions",
        "https://api.worldquantbrain.com/data-sets?limit=20&offset=0"
    ]
    
    for url in endpoints:
        print(f"\n==========================================")
        print(f"QUERYING: {url}")
        print(f"==========================================")
        try:
            r = session.get(url, timeout=30)
            print(f"Status Code: {r.status_code}")
            if r.status_code == 200:
                res = r.json()
                # Print a clean summary
                if "results" in res:
                    print(f"Results count: {len(res['results'])}")
                    for idx, item in enumerate(res['results'][:5]):
                        print(f"  [{idx+1}] {item.get('id') or item.get('name')}")
                else:
                    print(json.dumps(res, indent=2))
            else:
                print(r.text)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()

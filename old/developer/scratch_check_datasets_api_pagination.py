import json
from src.auth import WQSession

def main():
    session = WQSession()
    
    # Query /data-sets with no parameters
    url = "https://api.worldquantbrain.com/data-sets"
    print(f"Querying: {url}...")
    try:
        r = session.get(url, timeout=30)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            res = r.json()
            if isinstance(res, dict):
                print(f"Keys in response: {list(res.keys())}")
                print(f"Total count field: {res.get('count')}")
                results = res.get('results', [])
                print(f"Results list size returned: {len(results)}")
            else:
                print(f"Response is a list of size: {len(res)}")
        else:
            print(r.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

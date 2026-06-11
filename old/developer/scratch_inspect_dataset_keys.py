import json
from src.auth import WQSession

def main():
    session = WQSession()
    url = "https://api.worldquantbrain.com/data-sets/analyst4"
    r = session.get(url, timeout=30)
    if r.status_code == 200:
        res = r.json()
        print("Keys in API response:")
        for k in sorted(res.keys()):
            val = res[k]
            if not isinstance(val, (dict, list)):
                print(f"  {k}: {val}")
            else:
                print(f"  {k}: (type {type(val).__name__}, size {len(val)})")
        
        # Check if there are keys in the nested dictionary or fields
        print("\nChecking for subscription/access indicators:")
        for k, v in res.items():
            if any(term in k.lower() for term in ["sub", "access", "status", "allow", "perm"]):
                print(f"Found match: {k} -> {v}")
    else:
        print(f"Error {r.status_code}: {r.text}")

if __name__ == "__main__":
    main()

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.auth import WQSession

def main():
    session = WQSession(email="saineela731@gmail.com", password="iitg@123")
    try:
        session.load_persisted_cookies()
    except Exception as e:
        print(f"Failed to load cookies: {e}")
        return

    url = "https://api.worldquantbrain.com/simulations/z1sp7cYg5cab7RkTp4iDZR"
    try:
        r = session.get(url, timeout=15)
        if r.status_code == 200:
            res = r.json()
            print(json.dumps(res, indent=2))
        else:
            print(f"HTTP Error {r.status_code}: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

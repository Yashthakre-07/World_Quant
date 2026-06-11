import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

def main():
    env_path = Path("sai.env")
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print("Loaded sai.env")
    else:
        print("sai.env not found!")
        return

    email = os.getenv("WQ_EMAIL")
    password = os.getenv("WQ_PASSWORD")
    
    if not email or not password:
        print("Credentials missing in env!")
        return
        
    session = requests.Session()
    session.auth = (email, password)
    
    r = session.post("https://api.worldquantbrain.com/authentication")
    if r.status_code not in (200, 201):
        print("Auth failed!")
        return
    print("Authenticated successfully.")

    endpoints = [
        "users/self/history",
        "users/self/alphas",
        "users/self/simulations",
        "users/self",
        "alphas",
        "simulations",
    ]

    for ep in endpoints:
        url = f"https://api.worldquantbrain.com/{ep}"
        print(f"\n--- Trying GET {url} ---")
        res = session.get(url)
        print(f"GET Status Code: {res.status_code}")
        try:
            print(json.dumps(res.json(), indent=2)[:500])
        except Exception:
            print(res.text[:300])

        print(f"\n--- Trying POST {url} ---")
        res_post = session.post(url, json={})
        print(f"POST Status Code: {res_post.status_code}")
        try:
            print(json.dumps(res_post.json(), indent=2)[:500])
        except Exception:
            print(res_post.text[:300])

if __name__ == "__main__":
    main()

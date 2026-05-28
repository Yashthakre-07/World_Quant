import requests
from requests.auth import HTTPBasicAuth
import json

def test_credentials(env_file):
    print(f"\n--- Testing credentials from {env_file} ---")
    email = None
    password = None
    with open(env_file, "r") as f:
        for line in f:
            if line.startswith("WQ_EMAIL="):
                email = line.strip().split("=")[1]
            if line.startswith("WQ_PASSWORD="):
                password = line.strip().split("=")[1]
                
    print(f"Email: {email}")
    if not email or not password:
        print("Error: email or password missing.")
        return
        
    session = requests.Session()
    session.auth = HTTPBasicAuth(email, password)
    
    # 1. Post to authentication endpoint
    try:
        r = session.post("https://api.worldquantbrain.com/authentication")
        print(f"Auth Status Code: {r.status_code}")
        print("Auth Response Body:")
        try:
            print(json.dumps(r.json(), indent=2))
        except:
            print(r.text)
            
        # 2. Get users/self using the session cookies
        if r.status_code in [200, 201]:
            # Temporarily clear auth to test if cookies alone are valid
            session.auth = None
            
            endpoints = [
                "users/self",
                "users/self/limits",
                "users/self/permissions",
                "users/self/status",
                "users/self/tier",
                "users/self/profile"
            ]
            for ep in endpoints:
                url = f"https://api.worldquantbrain.com/{ep}"
                u = session.get(url)
                print(f"\n--- GET {url} ---")
                print(f"Status Code: {u.status_code}")
                try:
                    print(json.dumps(u.json(), indent=2))
                except:
                    print(u.text[:200])
            
    except Exception as e:
        print(f"Error: {e}")

test_credentials("sai.env")
test_credentials("yash.env")

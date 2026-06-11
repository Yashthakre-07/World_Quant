import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

def main():
    # Load sai.env
    env_path = Path(__file__).resolve().parent / "sai.env"
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
        
    print(f"Authenticating for {email}...")
    
    session = requests.Session()
    session.auth = (email, password)
    
    # Authenticate
    r = session.post("https://api.worldquantbrain.com/authentication")
    print(f"Auth Status: {r.status_code}")
    try:
        print(f"Auth Response: {json.dumps(r.json(), indent=2)}")
    except Exception:
        print(f"Auth Response Text: {r.text}")
        
    if r.status_code not in (200, 201):
        print("Auth failed!")
        return
        
    # Get self info
    r_self = session.get("https://api.worldquantbrain.com/users/self")
    print(f"\n/users/self Status: {r_self.status_code}")
    try:
        self_data = r_self.json()
        print(f"User Profile Info:\n{json.dumps(self_data, indent=2)}")
    except Exception:
        print(f"Response: {r_self.text}")

if __name__ == "__main__":
    main()

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
    else:
        print("sai.env not found!")
        return

    email = os.getenv("WQ_EMAIL")
    password = os.getenv("WQ_PASSWORD")
    
    session = requests.Session()
    session.auth = (email, password)
    
    r = session.post("https://api.worldquantbrain.com/authentication")
    if r.status_code not in (200, 201):
        print("Auth failed!")
        return

    url = "https://api.worldquantbrain.com/users/self/alphas"
    res = session.get(url, params={"limit": 5})
    if res.status_code == 200:
        data = res.json()
        print("Count:", data.get("count"))
        results = data.get("results", [])
        if results:
            print("\nKeys:", list(results[0].keys()))
            print("\nSample Item:")
            print(json.dumps(results[0], indent=2))
            
            # Let's print unique values of 'stage' or 'status' or other fields in the first 50 results
            res2 = session.get(url, params={"limit": 100})
            r_data = res2.json().get("results", [])
            stages = set()
            statuses = set()
            for x in r_data:
                if 'stage' in x: stages.add(str(x['stage']))
                if 'status' in x: statuses.add(str(x['status']))
                if 'state' in x: statuses.add(str(x['state']))
            print("\nStages found in first 100:", stages)
            print("Statuses found in first 100:", statuses)
    else:
        print("Failed:", res.status_code, res.text)

if __name__ == "__main__":
    main()

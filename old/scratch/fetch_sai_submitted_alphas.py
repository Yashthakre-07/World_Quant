import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

def main():
    # Load sai.env
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
        
    print(f"Authenticating for {email}...")
    
    session = requests.Session()
    session.auth = (email, password)
    
    # Authenticate
    r = session.post("https://api.worldquantbrain.com/authentication")
    if r.status_code not in (200, 201):
        print(f"Auth failed with status {r.status_code}: {r.text}")
        return
        
    print("Authentication successful.")
    
    # Fetch alphas
    # Let's request all alphas with pagination or high limit
    url = "https://api.worldquantbrain.com/alphas"
    params = {
        "limit": 100,
        "offset": 0
    }
    
    all_alphas = []
    
    while True:
        print(f"Fetching alphas, offset: {params['offset']}...")
        res = session.get(url, params=params)
        if res.status_code != 200:
            print(f"Failed to fetch alphas: {res.status_code} - {res.text}")
            break
            
        data = res.json()
        results = data.get("results", [])
        if not results:
            break
            
        all_alphas.extend(results)
        if len(results) < params["limit"]:
            break
        params["offset"] += params["limit"]
        
    print(f"\nFetched total of {len(all_alphas)} alphas.")
    
    # Filter for submitted alphas
    # Let's inspect the fields in the first alpha to understand status / stage representation
    if all_alphas:
        print("\nSample Alpha structure keys:", list(all_alphas[0].keys()))
        print("Sample Alpha status/stage:", {k: all_alphas[0].get(k) for k in ["status", "stage", "state"] if k in all_alphas[0]})
        
    submitted_alphas = []
    for a in all_alphas:
        # Check different possible status fields
        stage = a.get("stage")
        status = a.get("status")
        state = a.get("state")
        
        # Typically WorldQuant Brain uses stage == 'SUBMITTED' or status == 'SUBMITTED'
        if stage == "SUBMITTED" or status == "SUBMITTED" or state == "SUBMITTED" or a.get("isSubmitted") is True:
            submitted_alphas.append(a)
            
    print(f"\nFound {len(submitted_alphas)} submitted alphas:")
    print("=" * 100)
    for idx, a in enumerate(submitted_alphas, 1):
        alpha_id = a.get("id")
        formula = a.get("regular", {}).get("code") or a.get("formula")
        settings = a.get("settings", {})
        region = settings.get("region")
        universe = settings.get("universe")
        sharpe = a.get("is", {}).get("sharpe")
        fitness = a.get("is", {}).get("fitness")
        turnover = a.get("is", {}).get("turnover")
        if turnover is not None:
            turnover_str = f"{turnover*100:.2f}%"
        else:
            turnover_str = "N/A"
            
        print(f"{idx:03d} | ID: {alpha_id} | Sharpe: {sharpe} | Fitness: {fitness} | Turnover: {turnover_str} | Region: {region} | Universe: {universe}")
        print(f"      Formula: {formula}")
        print("-" * 100)

if __name__ == "__main__":
    main()

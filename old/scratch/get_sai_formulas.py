import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

def main():
    # Load credentials
    env_path = Path("sai.env")
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print("[*] Loaded sai.env credentials.")
    else:
        print("[-] sai.env credentials not found!")
        return

    email = os.getenv("WQ_EMAIL")
    password = os.getenv("WQ_PASSWORD")
    
    if not email or not password:
        print("[-] Credentials missing in env!")
        return
        
    print(f"[*] Authenticating with WorldQuant Brain for {email}...")
    
    session = requests.Session()
    session.auth = (email, password)
    
    r = session.post("https://api.worldquantbrain.com/authentication")
    if r.status_code not in (200, 201):
        print(f"[-] Authentication failed: {r.status_code} - {r.text}")
        return
    print("[+] WorldQuant Brain Session authenticated successfully.")

    # Fetch alphas from Render review queue
    print("[*] Fetching alphas from Render queue...")
    render_url = "https://world-quant.onrender.com/api/alphas"
    headers = {"Authorization": "Bearer yashthakreop"}
    
    try:
        res = requests.get(render_url, headers=headers, timeout=30, verify=False)
        if res.status_code != 200:
            print(f"[-] Failed to fetch from Render queue: {res.status_code}")
            return
        data = res.json()
    except Exception as e:
        print(f"[-] Error querying Render queue: {e}")
        return

    alphas = data.get("alphas", [])
    submitted_alphas = [a for a in alphas if a.get("status") == "SUBMITTED"]
    print(f"[+] Found {len(submitted_alphas)} submitted alphas in the Render review board.")
    
    print("\nRetrieving formulas from WorldQuant Brain...")
    
    records = []
    for idx, a in enumerate(submitted_alphas, 1):
        alpha_id = a.get("alpha_id")
        print(f"[{idx}/{len(submitted_alphas)}] Fetching details for {alpha_id}...", end="", flush=True)
        
        # Query WQ Brain for formula
        wq_url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
        wq_res = session.get(wq_url)
        if wq_res.status_code == 200:
            wq_data = wq_res.json()
            formula = wq_data.get("regular", {}).get("code") or wq_data.get("formula") or "N/A"
            settings = wq_data.get("settings", {})
            region = settings.get("region", "N/A")
            universe = settings.get("universe", "N/A")
            decay = settings.get("decay", "N/A")
            neutralization = settings.get("neutralization", "N/A")
            delay = settings.get("delay", "N/A")
            
            # Extract stats
            is_stats = wq_data.get("is", {})
            sharpe = is_stats.get("sharpe", a.get("sharpe"))
            fitness = is_stats.get("fitness", a.get("fitness"))
            turnover = is_stats.get("turnover", a.get("turnover"))
            if isinstance(turnover, float) and turnover < 1.0:
                turnover = turnover * 100 # Convert to percentage if it's decimal
            
            records.append({
                "alpha_id": alpha_id,
                "sharpe": sharpe,
                "fitness": fitness,
                "turnover": turnover,
                "region": region,
                "universe": universe,
                "decay": decay,
                "neutralization": neutralization,
                "delay": delay,
                "formula": formula
            })
            print(" Done.")
        else:
            print(f" Failed (Status: {wq_res.status_code})")
            records.append({
                "alpha_id": alpha_id,
                "sharpe": a.get("sharpe"),
                "fitness": a.get("fitness"),
                "turnover": a.get("turnover"),
                "region": "Unknown",
                "universe": "Unknown",
                "decay": "Unknown",
                "neutralization": "Unknown",
                "delay": "Unknown",
                "formula": "API Access Error / Not Found"
            })
            
    print("\n" + "=" * 100)
    print(f"SUBMITTED ALPHAS FOR {email} (Total: {len(records)}):")
    print("=" * 100)
    
    for idx, r in enumerate(records, 1):
        print(f"#{idx:02d} | Alpha ID: {r['alpha_id']} | Sharpe: {r['sharpe']:.2f} | Fitness: {r['fitness']:.2f} | Turnover: {r['turnover']:.2f}%")
        print(f"     Settings: Region: {r['region']} | Universe: {r['universe']} | Neutralization: {r['neutralization']} | Decay: {r['decay']} | Delay: {r['delay']}")
        print(f"     Formula:  {r['formula']}")
        print("-" * 100)

if __name__ == "__main__":
    main()

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
        print("[*] Loaded sai.env credentials.")
    else:
        print("[-] sai.env credentials not found!")
        return

    # Import WQSession from project src.auth
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.auth import WQSession

    print(f"[*] Initializing WQSession for saineela731@gmail.com...")
    session = WQSession(email="saineela731@gmail.com", password="iitg@123")
    
    # Check if session is authenticated
    if session.login_expired:
        print("[-] Persisted session cookies are expired or invalid, and biometric verification is required.")
        return
        
    print("[+] WQSession initialized successfully.")

    url = "https://api.worldquantbrain.com/users/self/alphas"
    limit = 100
    offset = 0
    
    filtered_alphas = []
    
    print("[*] Fetching all alphas from WQ Brain (this may take a minute since there are 3779 total)...")
    
    while True:
        res = session.get(url, params={"limit": limit, "offset": offset})
        if res.status_code != 200:
            print(f"\n[-] Error fetching alphas at offset {offset}: {res.status_code}")
            break
            
        data = res.json()
        results = data.get("results", [])
        if not results:
            break
            
        for item in results:
            date_sub = item.get("dateSubmitted")
            if date_sub:
                # Format is typically "2025-07-29T15:38:50..."
                # We want 2025 and early 2026 (e.g. before May 2026)
                if "2025-" in date_sub or "2026-01-" in date_sub or "2026-02-" in date_sub or "2026-03-" in date_sub or "2026-04-" in date_sub:
                    filtered_alphas.append(item)
                    
        print(f"\rParsed {offset + len(results)} / {data.get('count', 3779)} alphas. Found {len(filtered_alphas)} matching criteria...", end="", flush=True)
        
        if len(results) < limit:
            break
        offset += limit
        
    print(f"\n\n[+] Done parsing. Found {len(filtered_alphas)} alphas submitted in 2025 or early 2026.")
    
    # Organize fields and write to file
    formatted_list = []
    for item in filtered_alphas:
        alpha_id = item.get("id")
        date_sub = item.get("dateSubmitted")
        formula = item.get("regular", {}).get("code") or item.get("formula")
        settings = item.get("settings", {})
        region = settings.get("region", "N/A")
        universe = settings.get("universe", "N/A")
        decay = settings.get("decay", "N/A")
        neutralization = settings.get("neutralization", "N/A")
        delay = settings.get("delay", "N/A")
        
        is_stats = item.get("is", {})
        sharpe = is_stats.get("sharpe")
        fitness = is_stats.get("fitness")
        turnover = is_stats.get("turnover")
        if isinstance(turnover, float) and turnover < 1.0:
            turnover = turnover * 100
            
        formatted_list.append({
            "alpha_id": alpha_id,
            "dateSubmitted": date_sub,
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
        
    output_file = Path("scratch/sai_alphas_2025_2026.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(formatted_list, f, indent=2)
    print(f"[SUCCESS] Saved filtered alphas report to: {output_file}")
    
    # Print a summary of the first 50 matched alphas
    print("\n" + "=" * 120)
    print(f"SAMPLE OF SUBMITTED ALPHAS FOR saineela731@gmail.com FROM 2025 & EARLY 2026 (Total matched: {len(formatted_list)}):")
    print("=" * 120)
    for idx, r in enumerate(formatted_list[:50], 1):
        print(f"#{idx:02d} | ID: {r['alpha_id']} | Date: {r['dateSubmitted'][:10]} | Sharpe: {r['sharpe']} | Fitness: {r['fitness']} | Turnover: {r['turnover']:.2f}%")
        print(f"     Settings: Region: {r['region']} | Universe: {r['universe']} | Neut: {r['neutralization']} | Decay: {r['decay']} | Delay: {r['delay']}")
        print(f"     Formula:  {r['formula']}")
        print("-" * 120)
        
if __name__ == "__main__":
    main()

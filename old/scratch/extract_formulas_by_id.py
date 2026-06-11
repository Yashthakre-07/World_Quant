import os
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

    # Build local database of IDs to formulas from all JSON files in the workspace
    local_formula_map = {}
    
    print("[*] Indexing local JSON files for ID-to-Formula mappings...")
    root_dir = Path(".")
    json_paths = list(root_dir.glob("**/*.json"))
    for jp in json_paths:
        try:
            with open(jp, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            def scan_obj(obj):
                if isinstance(obj, dict):
                    aid = obj.get("alpha_id") or obj.get("id")
                    
                    # Safely handle formula key
                    formula = None
                    if "formula" in obj:
                        formula = obj["formula"]
                    elif "regular" in obj:
                        reg = obj["regular"]
                        if isinstance(reg, dict):
                            formula = reg.get("code")
                        elif isinstance(reg, str):
                            formula = reg
                    
                    if aid and formula and isinstance(formula, str):
                        local_formula_map[str(aid).strip()] = formula.strip()
                        
                    for k, v in obj.items():
                        if isinstance(v, (dict, list)):
                            scan_obj(v)
                elif isinstance(obj, list):
                    for item in obj:
                        scan_obj(item)
            
            scan_obj(content)
        except Exception:
            pass
            
    print(f"[+] Indexed {len(local_formula_map)} unique local ID -> Formula mappings.")

    # Combine online fetching and local mapping
    records = []
    for idx, a in enumerate(submitted_alphas, 1):
        alpha_id = a.get("alpha_id")
        print(f"[{idx}/{len(submitted_alphas)}] Checking {alpha_id}...", end="", flush=True)
        
        formula = None
        region = "USA"
        universe = "TOP3000"
        decay = 10
        neutralization = "SUBINDUSTRY"
        delay = 1
        
        # 1. Try fetching from WQ Brain
        wq_url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
        wq_res = session.get(wq_url)
        if wq_res.status_code == 200:
            wq_data = wq_res.json()
            formula = wq_data.get("regular", {}).get("code") or wq_data.get("formula")
            settings = wq_data.get("settings", {})
            region = settings.get("region", region)
            universe = settings.get("universe", universe)
            decay = settings.get("decay", decay)
            neutralization = settings.get("neutralization", neutralization)
            delay = settings.get("delay", delay)
            print(" WQ API Success.")
        else:
            # 2. Try looking up in local index
            local_form = local_formula_map.get(alpha_id)
            if local_form:
                formula = local_form
                print(" Local Cache Match.")
            else:
                print(" Not Found.")
                formula = "Unknown / API and Cache Miss"
                
        # Extract stats
        is_stats = wq_res.json().get("is", {}) if wq_res.status_code == 200 else {}
        sharpe = is_stats.get("sharpe", a.get("sharpe"))
        fitness = is_stats.get("fitness", a.get("fitness"))
        turnover = is_stats.get("turnover", a.get("turnover"))
        if isinstance(turnover, float) and turnover < 1.0:
            turnover = turnover * 100
            
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
            
    print("\n" + "=" * 120)
    print(f"SUBMITTED ALPHAS FOR {email} (Total: {len(records)}):")
    print("=" * 120)
    
    for idx, r in enumerate(records, 1):
        print(f"#{idx:02d} | Alpha ID: {r['alpha_id']} | Sharpe: {r['sharpe']:.2f} | Fitness: {r['fitness']:.2f} | Turnover: {r['turnover']:.2f}%")
        print(f"     Settings: Region: {r['region']} | Universe: {r['universe']} | Neutralization: {r['neutralization']} | Decay: {r['decay']} | Delay: {r['delay']}")
        print(f"     Formula:  {r['formula']}")
        print("-" * 120)

if __name__ == "__main__":
    main()

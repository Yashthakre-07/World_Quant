import os
import sys
import time
import argparse
import urllib3
from pathlib import Path
from dotenv import load_dotenv

# Clear proxy/IDE CA cert overrides that break Python SSL verification locally
os.environ.pop("REQUESTS_CA_BUNDLE", None)
os.environ.pop("SSL_CERT_FILE", None)
os.environ.pop("CURL_CA_BUNDLE", None)

# Add workspace directory to path
sys.path.append("c:/Users/Admin/Documents/VIBE_YT/wq")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from src.auth import WQSession
from src.client import WQClient

SERVERS = {
    "sai": {
        "name": "Sai's Account",
        "env_file": "sai.env"
    },
    "yash": {
        "name": "Yash's Account",
        "env_file": "yash.env"
    }
}

def load_account_env(account_key):
    server_conf = SERVERS[account_key]
    env_file = server_conf["env_file"]
    env_path = Path("c:/Users/Admin/Documents/VIBE_YT/wq") / env_file
    
    if not env_path.exists():
        print(f"[ERROR] Environment file '{env_file}' not found!")
        sys.exit(1)
        
    import src.config
    import src.auth
    
    print(f"[ENV] Loading environment variables from {env_file}...")
    load_dotenv(env_path, override=True)
    
    src.config.WQ_EMAIL = os.getenv("WQ_EMAIL", "")
    src.config.WQ_PASSWORD = os.getenv("WQ_PASSWORD", "")
    src.auth.WQ_EMAIL = src.config.WQ_EMAIL
    src.auth.WQ_PASSWORD = src.config.WQ_PASSWORD
    
    if not src.config.WQ_EMAIL or not src.config.WQ_PASSWORD:
        print(f"[ERROR] WQ_EMAIL or WQ_PASSWORD not defined in {env_file}!")
        sys.exit(1)
        
    print(f"[USER] Target Account: {src.config.WQ_EMAIL}")

def main():
    parser = argparse.ArgumentParser(description="AlphaForge Direct Platform Submission Tool")
    parser.add_argument("--account", choices=["sai", "yash"], help="Which account to run submission for (sai or yash)")
    parser.add_argument("--min-sharpe", type=float, default=1.25, help="Minimum Sharpe ratio to submit (default: 1.25)")
    parser.add_argument("--min-fitness", type=float, default=0.9, help="Minimum Fitness score to submit (default: 0.9)")
    parser.add_argument("--auto", action="store_true", help="Automatically submit all candidates without prompting")
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of submissions to attempt in this run")
    
    args = parser.parse_args()
    
    account = args.account
    if not account:
        print("Available accounts:")
        for k, v in SERVERS.items():
            print(f"  - {k}: {v['name']}")
        account = input("Select account (sai/yash): ").strip().lower()
        while account not in SERVERS:
            account = input("Invalid selection. Choose 'sai' or 'yash': ").strip().lower()
            
    print(f"\n==========================================")
    print(f"Direct WQ Platform Submission: {SERVERS[account]['name']}")
    print(f"==========================================")
    
    # 1. Load env variables
    load_account_env(account)
    
    # 2. Authenticate session in CLI mode
    print("\n[AUTH] Authenticating with WorldQuant Brain platform...")
    try:
        session = WQSession(interactive=True, cli_mode=True)
        client = WQClient(session)
        print("[AUTH] Authentication successful!")
    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}")
        sys.exit(1)
        
    # 3. Fetch alphas directly from WQ Brain API
    url = "https://api.worldquantbrain.com/users/self/alphas"
    params = {"limit": 100}
    print("[API] Fetching all alphas directly from WQ account...")
    
    alphas = []
    while url:
        try:
            r = session.get(url, params=params, timeout=30)
            if r.status_code != 200:
                print(f"[ERROR] Failed to fetch alphas: HTTP {r.status_code}: {r.text}")
                break
            res = r.json()
            alphas.extend(res.get("results", []))
            
            url = None
            links = res.get("links", [])
            for link in links:
                if link.get("rel") == "next":
                    url = link.get("href")
                    params = None
                    break
        except Exception as e:
            print(f"[ERROR] Error during pagination fetch: {e}")
            break
            
    print(f"[SUCCESS] Retrieved {len(alphas)} total alphas from account.")
    
    # 4. Scan for candidates
    candidates = []
    print("\n[SCAN] Scanning for qualifying unsubmitted candidate alphas...")
    for a in alphas:
        status = a.get("status")
        alpha_id = a.get("id")
        
        if status == "UNSUBMITTED":
            metrics = a.get("is", {})
            sharpe = metrics.get("sharpe")
            fitness = metrics.get("fitness")
            turnover = metrics.get("turnover", 0.0) * 100.0 if metrics.get("turnover") is not None else 0.0
            
            # Check weight concentration
            weight_pass = True
            checks = metrics.get("checks", [])
            for c in checks:
                if c.get("name") == "CONCENTRATED_WEIGHT" and c.get("result") == "FAIL":
                    weight_pass = False
                    
            if (sharpe is not None and sharpe >= args.min_sharpe) and \
               (fitness is not None and fitness >= args.min_fitness) and \
               (1.0 <= turnover <= 70.0) and weight_pass:
                candidates.append(a)
                print(f"  Candidate: ID {alpha_id} | Sharpe: {sharpe:.2f} | Fitness: {fitness:.2f} | Turnover: {turnover:.1f}% | Formula: {a.get('regular', {}).get('code')}")
                
    if not candidates:
        print("\n[INFO] No qualifying unsubmitted candidates found meeting requirements.")
        sys.exit(0)
        
    # Limit number of submissions
    candidates = candidates[:args.limit]
    print(f"\n[QUEUE] Found {len(candidates)} candidates ready for submission.")
    
    if not args.auto:
        confirm = input(f"Proceed to submit these {len(candidates)} candidate(s) to production? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Submission cancelled.")
            sys.exit(0)
            
    submitted_count = 0
    failed_count = 0
    
    for idx, c in enumerate(candidates):
        alpha_id = c.get("id")
        formula = c.get("regular", {}).get("code")
        print(f"\n--- [{idx+1}/{len(candidates)}] Submitting Alpha ID: {alpha_id} ---")
        print(f"  Formula: {formula}")
        
        # Trigger submission
        res = client.submit_alpha(alpha_id)
        
        if res.get("success"):
            print(f"[SUCCESS] Alpha {alpha_id} submitted successfully!")
            submitted_count += 1
            
            # Color RED on platform
            try:
                color_r = session.patch(f"https://api.worldquantbrain.com/alphas/{alpha_id}", json={"color": "RED"}, timeout=15)
                if color_r.status_code == 200:
                    print(f"  [COLOR] Colored RED on platform successfully.")
                else:
                    print(f"  [WARN] Failed to color RED: {color_r.text}")
            except Exception as e:
                print(f"  [WARN] Error coloring RED: {e}")
                
            # Add a small delay between submissions to respect rate limits
            time.sleep(5)
        else:
            print(f"[FAILED] Submission rejected for {alpha_id}: {res.get('details')}")
            failed_count += 1
            
    print(f"\n==========================================")
    print(f"DIRECT SUBMISSION SUMMARY")
    print(f"==========================================")
    print(f"Account: {os.getenv('WQ_EMAIL')}")
    print(f"Attempted: {submitted_count + failed_count}")
    print(f"Successfully Submitted: {submitted_count}")
    print(f"Failed/Rejected: {failed_count}")
    print(f"==========================================")

if __name__ == "__main__":
    main()

import os
import sys
import argparse
import time
import urllib.request
import json
import ssl
from pathlib import Path
from dotenv import load_dotenv

# Disable SSL verification issues for self-signed certificates or proxy servers
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Server configurations
SERVERS = {
    "sai": {
        "name": "Sai's Account",
        "url": "https://world-quant.onrender.com",
        "token": "yashthakreop",
        "env_file": "sai.env"
    },
    "yash": {
        "name": "Yash's Account",
        "url": "https://world-quant-1.onrender.com",
        "token": "yashthakreop1",
        "env_file": "yash.env"
    }
}

def load_account_env(account_key):
    server_conf = SERVERS[account_key]
    env_file = server_conf["env_file"]
    env_path = Path(__file__).resolve().parent / env_file
    
    if not env_path.exists():
        print(f"[ERROR] Environment file '{env_file}' not found at {env_path}")
        sys.exit(1)
        
    # Import config first to let it do its default loading, then override it
    import src.config
    
    print(f"[ENV] Loading environment variables from {env_file}...")
    load_dotenv(env_path, override=True)
    
    # Set explicit configuration in src.config manually
    src.config.WQ_EMAIL = os.getenv("WQ_EMAIL", "")
    src.config.WQ_PASSWORD = os.getenv("WQ_PASSWORD", "")
    
    if not src.config.WQ_EMAIL or not src.config.WQ_PASSWORD:
        print(f"[ERROR] WQ_EMAIL or WQ_PASSWORD not defined in {env_file}!")
        sys.exit(1)
        
    print(f"[USER] Target Account: {src.config.WQ_EMAIL}")

def fetch_successful_alphas(account_key):
    server_conf = SERVERS[account_key]
    url = f"{server_conf['url']}/api/alphas"
    token = server_conf['token']
    
    print(f"[API] Fetching successful simulated alphas from server: {server_conf['url']}...")
    
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            res_body = response.read().decode("utf-8")
            data = json.loads(res_body)
            alphas = data.get("alphas", [])
            print(f"[SUCCESS] Successfully fetched {len(alphas)} completed alphas from server.")
            return alphas
    except Exception as e:
        print(f"[ERROR] Failed to fetch alphas from server: {e}")
        sys.exit(1)

def fetch_alpha_detail(account_key, alpha_id):
    server_conf = SERVERS[account_key]
    url = f"{server_conf['url']}/api/alpha/{alpha_id}"
    token = server_conf['token']
    
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body)
    except Exception as e:
        print(f"[WARN] Warning: Could not fetch details for alpha {alpha_id}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="AlphaForge Manual Submission Tool")
    parser.add_argument("--account", choices=["sai", "yash"], help="Which account to run submission for (sai or yash)")
    parser.add_argument("--min-sharpe", type=float, default=1.25, help="Minimum Sharpe ratio to submit (default: 1.25)")
    parser.add_argument("--min-fitness", type=float, default=0.8, help="Minimum Fitness score to submit (default: 0.8)")
    parser.add_argument("--auto", action="store_true", help="Automatically submit all candidates without prompting")
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of submissions to attempt in this run")
    
    args = parser.parse_args()
    
    # Prompt if account not provided
    account = args.account
    if not account:
        print("Available accounts:")
        for k, v in SERVERS.items():
            print(f"  - {k}: {v['name']} ({v['url']})")
        account = input("Select account (sai/yash): ").strip().lower()
        while account not in SERVERS:
            account = input("Invalid selection. Please choose 'sai' or 'yash': ").strip().lower()
            
    print(f"\n==========================================")
    print(f"AlphaForge Manual Submission: {SERVERS[account]['name']}")
    print(f"==========================================")
    
    # 1. Load account credentials
    load_account_env(account)
    
    # Import src modules after setting environment
    from src.auth import WQSession
    from src.client import WQClient
    
    # 2. Authenticate locally with interactive support (allows browser verification)
    print("\n[AUTH] Authenticating with WorldQuant Brain platform...")
    try:
        session = WQSession(interactive=True, cli_mode=True)
        client = WQClient(session)
        print("[AUTH] Session successfully established and verified!")
    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}")
        sys.exit(1)
        
    # 3. Fetch list of alphas from server
    raw_alphas = fetch_successful_alphas(account)
    
    # Filter candidate soft-failed alphas
    candidates = []
    print("\n[SCAN] Scanning for manual submission candidates...")
    
    for a in raw_alphas:
        status = a.get("status")
        if status != "SUBMITTED":
            sharpe = a.get("sharpe") or 0.0
            fitness = a.get("fitness") or 0.0
            turnover = a.get("turnover") or 0.0
            
            # Submittable criteria: Sharpe >= min-sharpe, Fitness >= min-fitness, Turnover between 1.0% and 70.0%
            if sharpe >= args.min_sharpe and fitness >= args.min_fitness and 1.0 <= turnover <= 70.0:
                candidates.append(a)
                
    print(f"[INFO] Found {len(candidates)} high-quality soft-failed candidates meeting requirements (Sharpe >= {args.min_sharpe}, Fitness >= {args.min_fitness}):")
    for idx, c in enumerate(candidates):
        print(f"  [{idx+1:2d}] ID: {c.get('alpha_id')} | Sharpe: {c.get('sharpe'):.2f} | Fitness: {c.get('fitness'):.2f} | Turnover: {c.get('turnover'):.2f}% | Family: {c.get('family')}")
        
    if not candidates:
        print("\n[INFO] No new candidates to submit! All eligible alphas have already been submitted or none match the criteria.")
        sys.exit(0)
        
    # Limit number of submissions
    candidates = candidates[:args.limit]
    print(f"\n[QUEUE] Proceeding with up to {len(candidates)} candidate submissions.")
    
    submitted_count = 0
    failed_count = 0
    
    for idx, c in enumerate(candidates):
        alpha_id = c.get("alpha_id")
        print(f"\n--- [{idx+1}/{len(candidates)}] Submitting Candidate Alpha ID: {alpha_id} ---")
        
        # Fetch detailed formula to print for user verification
        detail = fetch_alpha_detail(account, alpha_id)
        if detail:
            print(f"  Formula: {detail.get('formula')}")
            print(f"  Family: {detail.get('family')}")
            print(f"  Stats: Sharpe={detail.get('sharpe')}, Fitness={detail.get('fitness')}, Turnover={detail.get('turnover')}%")
            
        if not args.auto:
            choice = input(f"Confirm submission of {alpha_id} to production? (y/n/skip/exit): ").strip().lower()
            if choice == "exit":
                print("Exiting submission pipeline.")
                break
            elif choice in ("n", "skip"):
                print("Skipping this alpha.")
                continue
                
        # Trigger submission via API
        print(f"[SUBMIT] Pushing {alpha_id} to WorldQuant Brain production queue...")
        res = client.submit_alpha(alpha_id)
        
        if res.get("success"):
            print(f"[SUCCESS] Alpha {alpha_id} submitted successfully! Details: {res.get('details')}")
            submitted_count += 1
            # Add a small delay between submissions to respect rate limits
            time.sleep(5)
        else:
            print(f"[FAILED] Submission rejected for {alpha_id}: {res.get('details')}")
            failed_count += 1
            
    print(f"\n==========================================")
    print(f"SUBMISSION SESSION SUMMARY")
    print(f"==========================================")
    print(f"Account: {os.getenv('WQ_EMAIL')}")
    print(f"Attempted: {submitted_count + failed_count}")
    print(f"Successfully Submitted: {submitted_count}")
    print(f"Failed/Rejected: {failed_count}")
    print(f"==========================================")

if __name__ == "__main__":
    main()

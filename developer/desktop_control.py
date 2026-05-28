import os
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

# Color codes for premium terminal feedback
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

# ── Dual-Server Configuration ─────────────────────────────────────────────────
SERVERS = {
    "1": {
        "name": "🔵 Sai's Server  (world-quant)",
        "url":   "https://world-quant.onrender.com",
        "token": "yashthakreop",
        "account": "saineela731@gmail.com",
    },
    "2": {
        "name": "🟢 Yash's Server (world-quant-1)",
        "url":   "https://world-quant-1.onrender.com",
        "token": "yashthakreop1",
        "account": "beyondsynapse@gmail.com",
    },
}

SERVER_URL = SERVERS["1"]["url"]
API_TOKEN  = SERVERS["1"]["token"]

def print_header(title):
    print(f"\n{BOLD}{MAGENTA}" + "="*60)
    print(f" {title.center(58)}")
    print("="*60 + f"{RESET}\n")

def make_request(path, method="GET", data=None):
    url = f"{SERVER_URL.rstrip('/')}{path}"
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode("utf-8")
        
    req = urllib.request.Request(url, data=req_data, method=method)
    req.add_header("Authorization", f"Bearer {API_TOKEN}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body), response.status
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        try:
            return json.loads(err_msg), e.code
        except Exception:
            return {"error": err_msg or e.reason}, e.code
    except urllib.error.URLError as e:
        return {"error": f"Failed to connect to server: {e.reason}"}, 500
    except Exception as e:
        return {"error": str(e)}, 500

def check_status():
    print_header("📊 SERVER STATE & PIPELINE TELEMETRY")
    print(f"{BLUE}Contacting cloud server at {SERVER_URL}...{RESET}")
    res, status = make_request("/api/queue-status")
    if status == 200:
        p_status = res.get("pipeline_status", "UNKNOWN")
        status_color = GREEN if p_status == "RUNNING" else (YELLOW if p_status == "PAUSED" else RED)
        
        print(f"{BOLD}Pipeline Status: {status_color}{p_status}{RESET}")
        print(f"{BOLD}Queue Count (On Disk): {CYAN}{res.get('queue_on_disk', 0)}{RESET}")
        print(f"{BOLD}Alphas In Memory:      {CYAN}{res.get('in_memory', 0)}{RESET}")
        
        formulas = res.get("formulas", [])
        if formulas:
            print(f"\n{BOLD}{YELLOW}Active Simulation Queue Preview:{RESET}")
            for idx, form in enumerate(formulas):
                print(f"  [{idx+1}] {form}...")
        else:
            print(f"\n{YELLOW}Queue is currently empty.{RESET}")
    else:
        print(f"{RED}Error fetching status (HTTP {status}): {res.get('error')}{RESET}")

def add_alpha():
    print_header("➕ ADD NEW COMPLIANT QUANT ALPHA")
    family = input(f"{BOLD}Enter Alpha Family Name:{RESET} ").strip()
    hypothesis = input(f"{BOLD}Enter Thesis/Hypothesis:{RESET} ").strip()
    formula = input(f"{BOLD}Enter Formula Expression:{RESET} ").strip()
    
    if not family or not formula:
        print(f"{RED}Error: Family name and Formula are required!{RESET}")
        return
        
    payload = [{
        "family": family,
        "hypothesis": hypothesis,
        "formula": formula,
        "settings": {
            "decay": 5, "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000", "truncation": 0.08
        }
    }]
    
    res, status = make_request("/api/queue-alpha", "POST", payload)
    if status in (200, 201):
        print(f"\n{GREEN}✔ SUCCESS! Alpha successfully queued on Render server.{RESET}")
        print(f"Server Message: {res.get('message', 'Queued.')}")
    else:
        print(f"\n{RED}❌ FAILED (HTTP {status}): {res.get('error')}{RESET}")

def overwrite_queue():
    print_header("🔄 OVERWRITE SIMULATION QUEUE")
    print(f"{YELLOW}WARNING: This will completely replace the current queue on the server!{RESET}\n")
    confirm = input("Are you absolutely sure? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
        
    formula = input(f"{BOLD}Enter Formula for single new queue item:{RESET} ").strip()
    family = input(f"{BOLD}Enter Family Name:{RESET} ").strip()
    hypothesis = input(f"{BOLD}Enter Hypothesis:{RESET} ").strip()
    
    if not formula:
        print(f"{RED}Formula cannot be empty!{RESET}")
        return
        
    payload = [{
        "family": family or "Manual Overwrite",
        "hypothesis": hypothesis or "Injected via desktop control deck",
        "formula": formula,
        "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
    }]
    
    res, status = make_request("/api/overwrite-queue", "POST", payload)
    if status == 200:
        print(f"\n{GREEN}✔ SUCCESS! Queue overwritten. Remaining queue size: {res.get('overwritten_count')}{RESET}")
    else:
        print(f"\n{RED}❌ FAILED (HTTP {status}): {res.get('error')}{RESET}")

def clean_queue():
    print_header("❌ REMOVE REJECTED/UNSUBMITTED ALPHAS")
    print(f"{BLUE}Initiating remote scan against failure vault database...{RESET}")
    res, status = make_request("/api/clean-queue", "POST", {})
    if status == 200:
        removed = res.get("removed_count", 0)
        print(f"\n{GREEN}✔ SUCCESS! Dynamic queue cleaned.{RESET}")
        print(f"Removed Alphas Count: {YELLOW}{removed}{RESET}")
        print(f"Remaining Alphas Left: {GREEN}{res.get('remaining_queue_count', 0)}{RESET}")
        if removed > 0:
            print(f"\n{BOLD}Removed Formulas:{RESET}")
            for formula in res.get("removed_formulas", []):
                print(f"  - {formula[:70]}...")
    else:
        print(f"\n{RED}❌ FAILED (HTTP {status}): {res.get('error')}{RESET}")

def control_pipeline(action):
    verb = "PAUSE" if action == "stop" else "RESUME"
    print_header(f"⏸️ {verb} REMOTE BACKTESTER PIPELINE")
    res, status = make_request(f"/api/{action}-pipeline", "POST", {})
    if status == 200:
        print(f"\n{GREEN}✔ SUCCESS! Remote pipeline has been {verb}D.{RESET}")
        print(f"Server Response: {YELLOW}{res.get('message')}{RESET}")
    else:
        print(f"\n{RED}❌ FAILED (HTTP {status}): {res.get('error')}{RESET}")

def sync_alphas():
    print_header("📥 SYNCHRONISE REMOTE ALPHAS TO LOCAL PC")
    print(f"{BLUE}Fetching list of simulated alphas from Render server...{RESET}")
    res, status = make_request("/api/alphas")
    
    if status != 200:
        print(f"{RED}Failed to list alphas (HTTP {status}): {res.get('error')}{RESET}")
        return
        
    remote_alphas = res.get("alphas", [])
    print(f"Found {YELLOW}{len(remote_alphas)}{RESET} successful simulated alphas on Render storage.\n")
    
    local_dir = Path(__file__).resolve().parent / "alphas"
    local_dir.mkdir(exist_ok=True)
    
    synced_count = 0
    skipped_count = 0
    
    for ra in remote_alphas:
        alpha_id = ra.get("alpha_id")
        if not alpha_id:
            continue
            
        filename = f"alpha_{alpha_id}.json"
        local_file = local_dir / filename
        
        # If file is not present locally, download it directly!
        if not local_file.exists():
            print(f"  {CYAN}Downloading {filename}...{RESET}")
            alpha_data, a_status = make_request(f"/api/alpha/{alpha_id}")
            if a_status == 200:
                with open(local_file, "w") as lf:
                    json.dump(alpha_data, lf, indent=2)
                print(f"  {GREEN}✔ Synced successfully.{RESET}")
                synced_count += 1
            else:
                print(f"  {RED}❌ Failed download for ID {alpha_id}: {alpha_data.get('error')}{RESET}")
        else:
            skipped_count += 1
            
    print(f"\n{BOLD}{GREEN}★ SYNC COMPLETE!{RESET}")
    print(f"  Synced (Downloaded): {GREEN}{synced_count}{RESET} new alphas")
    print(f"  Already existed:     {BLUE}{skipped_count}{RESET} alphas (skipped)")
    print(f"  Saved locally in:    {BOLD}{local_dir.resolve()}{RESET}")

def select_server():
    """Show server picker at startup."""
    global SERVER_URL, API_TOKEN
    print(f"\n{BOLD}{CYAN}" + "="*60)
    print(f"   SELECT TARGET SERVER".center(60))
    print("="*60 + f"{RESET}")
    for key, srv in SERVERS.items():
        print(f"  {BOLD}{key}.{RESET} {srv['name']}")
        print(f"      URL:     {CYAN}{srv['url']}{RESET}")
        print(f"      Account: {YELLOW}{srv['account']}{RESET}")
        print()
    choice = input(f"{BOLD}Pick server (1 / 2) [default: 1]: {RESET}").strip() or "1"
    srv = SERVERS.get(choice, SERVERS["1"])
    SERVER_URL = srv["url"]
    API_TOKEN  = srv["token"]
    print(f"\n{GREEN}✔ Targeting: {srv['name']}{RESET}")


def main_menu():
    global SERVER_URL, API_TOKEN
    os.system("color")  # Enable ANSI terminal coloring on Windows CMD/PowerShell
    select_server()

    while True:
        print(f"\n{BOLD}{YELLOW}" + "#"*60)
        print("   " + f"★ ALPHAFORGE DESKTOP QUANT DEV PANEL ★".center(54))
        print("   " + f"Direct Secure API Engine | Bypass GitHub".center(54))
        print("#"*60 + f"{RESET}")

        # Identify which named server we're on
        active_name = next((s["name"] for s in SERVERS.values() if s["url"] == SERVER_URL), SERVER_URL)
        print(f"\n{BOLD}Target Server: {CYAN}{active_name}{RESET}")
        print(f"{BOLD}URL:           {CYAN}{SERVER_URL}{RESET}")
        print(f"{BOLD}Token Active:  {GREEN}{API_TOKEN[:4]}...{API_TOKEN[-4:] if len(API_TOKEN) > 4 else ''}{RESET}\n")

        print(f" {BOLD}1.{RESET} 📊 Check Server Status & Active Queue")
        print(f" {BOLD}2.{RESET} ➕ Queue New Alpha (Append)")
        print(f" {BOLD}3.{RESET} ❌ Remove Rejected/Unsubmitted Alphas (API Clean)")
        print(f" {BOLD}4.{RESET} 🔄 Overwrite Simulation Queue Entirely")
        print(f" {BOLD}5.{RESET} ⏸️ Pause Pipeline Execution (Stop)")
        print(f" {BOLD}6.{RESET} ▶️ Resume Pipeline Execution (Restart)")
        print(f" {BOLD}7.{RESET} 📥 Synchronize Remote Alphas directly to PC")
        print(f" {BOLD}8.{RESET} 🔀 Switch Target Server")
        print(f" {BOLD}9.{RESET} 🚪 Exit Dev Deck")

        choice = input(f"\n{BOLD}Select Option (1-9):{RESET} ").strip()

        if choice == "1":
            check_status()
        elif choice == "2":
            add_alpha()
        elif choice == "3":
            clean_queue()
        elif choice == "4":
            overwrite_queue()
        elif choice == "5":
            control_pipeline("stop")
        elif choice == "6":
            control_pipeline("start")
        elif choice == "7":
            sync_alphas()
        elif choice == "8":
            select_server()
        elif choice == "9":
            print(f"\n{BOLD}{YELLOW}Shutting down Quant Dev Panel. Keep AlphaForge active!{RESET}\n")
            sys.exit(0)
        else:
            print(f"{RED}Invalid Option! Select a valid choice between 1 and 9.{RESET}")

        input(f"\nPress {BOLD}[Enter]{RESET} to return to main menu...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{RED}Session interrupted. Exiting.{RESET}")
        sys.exit(0)

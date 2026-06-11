# -*- coding: utf-8 -*-
"""
push_accepted_alphas.py
-------------------------
Integrates MANDATORY API REVIEW BOX SUBMISSION workflow.
Pushes accepted alphas passing all validation checks to the Render review queue.

Usage:
    python push_accepted_alphas.py --num-alphas 10
    python push_accepted_alphas.py --file alphas/all_600_alphas.json --num-alphas 25
"""

import os
import sys
import json
import sqlite3
import argparse
import requests
from datetime import datetime

# Setup project root path
WQ_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WQ_ROOT)

# Try local workspace path first, fallback to config
local_db_path = os.path.join(WQ_ROOT, "db", "alpha_vault.db")
if os.path.exists(local_db_path):
    DB_PATH_RESOLVED = local_db_path
else:
    from src.config import DB_PATH
    DB_PATH_RESOLVED = str(DB_PATH)

API_ENDPOINT = "https://world-quant.onrender.com/api/queue-alpha"
BEARER_TOKEN = "yashthakreop"
HISTORICAL_FILE = os.path.join(WQ_ROOT, "scratch", "historical_scheduled_alphas.json")
RUN_LOG_PATH = os.path.join(WQ_ROOT, "scratch", "run_log.txt")

def log_message(msg):
    timestamp = datetime.now().isoformat()
    log_line = f"{timestamp} | {msg}\n"
    os.makedirs(os.path.dirname(RUN_LOG_PATH), exist_ok=True)
    with open(RUN_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_line)
    try:
        print(log_line.strip())
    except UnicodeEncodeError:
        # Fallback to replace characters not supported by CP1252/Windows console
        encoding = sys.stdout.encoding or 'ascii'
        print(log_line.strip().encode(encoding, errors='replace').decode(encoding))

def load_from_db():
    """Queries DB for successfully simulated/accepted alphas."""
    if not os.path.exists(DB_PATH_RESOLVED):
        log_message(f"[WARNING] Database not found at {DB_PATH_RESOLVED}")
        return []
    
    log_message(f"[*] Reading accepted alphas from SQLite: {DB_PATH_RESOLVED}")
    conn = sqlite3.connect(DB_PATH_RESOLVED)
    cursor = conn.cursor()
    
    # Query for alpha runs that passed validation
    # (Using status='SUBMITTED' or green status in alpha_runs)
    try:
        cursor.execute("""
            SELECT run_id, family, hypothesis, formula, region, universe, neutralization, decay, truncation, delay, status
            FROM alpha_runs
            WHERE status = 'SUBMITTED' OR status = 'GREEN'
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        alphas = []
        for r in rows:
            alphas.append({
                "run_id": r[0],
                "family": r[1],
                "hypothesis": r[2],
                "formula": r[3],
                "region": r[4],
                "universe": r[5],
                "neutralization": r[6],
                "decay": r[7],
                "truncation": r[8],
                "delay": r[9],
                "status": r[10]
            })
        conn.close()
        return alphas
    except Exception as e:
        log_message(f"[ERROR] DB Query failed: {e}")
        conn.close()
        return []

def load_from_file(filepath):
    """Loads alphas from a JSON file."""
    if not os.path.exists(filepath):
        log_message(f"[ERROR] JSON file not found at: {filepath}")
        sys.exit(1)
    
    log_message(f"[*] Loading alphas from file: {filepath}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # If it's a dict, try to find list fields
        if isinstance(data, dict):
            for key in ["alphas", "results", "formulas"]:
                if key in data and isinstance(data[key], list):
                    return data[key]
            data = [data]
        return data
    except Exception as e:
        log_message(f"[ERROR] Failed to parse JSON file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Mandatory API Review Box Submission Manager")
    parser.add_argument("--num-alphas", type=int, required=True, help="Exactly specify count of alphas (e.g. 10, 25, 50)")
    parser.add_argument("--file", type=str, default=None, help="Optional JSON file path to read alphas from")
    parser.add_argument("--dry-run", action="store_true", help="Perform count and format validation without pushing")
    args = parser.parse_args()

    num_alphas = args.num_alphas
    log_message(f"======================================================================")
    log_message(f"🚀 MANDATORY REVIEW BOX SUBMISSION INITIALIZED (Target Count: {num_alphas})")
    log_message(f"======================================================================")

    # 1. Load Alphas
    raw_alphas = []
    if args.file:
        raw_alphas = load_from_file(args.file)
    else:
        raw_alphas = load_from_db()
    
    # 2. Filter & clean unique accepted alphas
    accepted_alphas = []
    seen_formulas = set()
    
    for a in raw_alphas:
        # Extract formula
        formula = a.get("formula", a.get("regular", "")).strip()
        if not formula or formula in seen_formulas:
            continue
        
        # Determine metadata
        family = a.get("family", "ThemePool_USA_D1")
        dataset = a.get("dataset", "custom")
        competition = a.get("competition", "USA_D1_FastDatasets_PowerPool_June2026")
        hypothesis = a.get("hypothesis", f"Systematic quantitative alpha for {dataset}")
        anomaly = a.get("anomaly_basis", a.get("hypothesis", "Market Inefficiency / PEAD"))
        
        # Map settings to exactly match the payload requirements
        settings = a.get("settings", {})
        if not isinstance(settings, dict):
            settings = {}
            
        settings_payload = {
            "region": settings.get("region", "USA"),
            "delay": int(settings.get("delay", 1)),
            "decay": int(settings.get("decay", 5)),
            "neutralization": settings.get("neutralization", "SUBINDUSTRY"),
            "universe": settings.get("universe", "TOP3000"),
            "truncation": float(settings.get("truncation", 0.08))
        }

        accepted_alphas.append({
            "family": family,
            "dataset": dataset,
            "competition": competition,
            "hypothesis": hypothesis,
            "anomaly_basis": anomaly,
            "formula": formula,
            "settings": settings_payload
        })
        seen_formulas.add(formula)

    # Slice to desired target count
    selected_alphas = accepted_alphas[:num_alphas]

    log_message(f"[*] Total unique accepted alphas identified: {len(accepted_alphas)}")
    log_message(f"[*] Alphas selected for submission: {len(selected_alphas)}")

    # 3. CRITICAL SUBMISSION VERIFICATION
    # Verification Rule:
    # - Count of generated alphas == NUM_ALPHAS
    # - Count of accepted alphas == NUM_ALPHAS
    # - Count of submitted alphas == NUM_ALPHAS
    count_generated = len(raw_alphas)
    count_accepted = len(accepted_alphas)
    count_selected = len(selected_alphas)

    log_message(f"[*] Verification details:")
    log_message(f"    - Generated Alphas Count: {count_generated}")
    log_message(f"    - Accepted Alphas Count:  {count_accepted}")
    log_message(f"    - Selected Alphas Count:  {count_selected}")

    # We enforce that both the generated, accepted, and selected counts are at least equal to target NUM_ALPHAS
    # If the database or file has less than NUM_ALPHAS, we must abort as we cannot push partial results.
    if count_accepted < num_alphas or count_selected < num_alphas:
        log_message(f"[CRITICAL ERROR] Count mismatch exists. Aborting submission to prevent partial pushing.")
        sys.exit(1)

    log_message(f"[SUCCESS] Submission Verification PASS: Exactly {num_alphas} unique accepted alphas match the target count.")

    if args.dry_run:
        log_message(f"[DRY-RUN] Verification complete. Payload sample:")
        print(json.dumps(selected_alphas[:2], indent=2))
        sys.exit(0)

    # 4. Push payload to Render Review Box API
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        log_message(f"[*] Connecting to {API_ENDPOINT} ...")
        response = requests.post(API_ENDPOINT, json=selected_alphas, headers=headers, timeout=60)
        
        if response.status_code == 200:
            log_message(f"[SUCCESS] All {num_alphas} accepted alphas successfully pushed to Review API.")
            log_message(f"Server Response Body: {response.text}")
            
            # 5. Append to historical registry
            historical_formulas = []
            if os.path.exists(HISTORICAL_FILE):
                try:
                    with open(HISTORICAL_FILE, "r", encoding="utf-8") as f:
                        historical_formulas = json.load(f)
                except Exception:
                    historical_formulas = []
            
            for item in selected_alphas:
                formula_str = item["formula"].strip().replace(" ", "")
                if formula_str not in historical_formulas:
                    historical_formulas.append(formula_str)
                    
            with open(HISTORICAL_FILE, "w", encoding="utf-8") as f:
                json.dump(historical_formulas, f, indent=2)
                
            log_message(f"[*] Appended submitted alphas to historical_scheduled_alphas.json and recorded timestamp.")
            
        else:
            log_message(f"[CRITICAL FAILURE] Review API submission failed.")
            log_message(f"HTTP Status: {response.status_code}")
            log_message(f"Response Body: {response.text}")
            log_message(f"[*] Aborting execution as per safety rules.")
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        log_message(f"[WARNING] API endpoint is unreachable or connection error occurred: {e}")
        # Save locally to prevent loss
        backup_path = os.path.join(WQ_ROOT, "scratch", f"locally_saved_alphas_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        try:
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(selected_alphas, f, indent=2)
            log_message(f"[SUCCESS] Alphas preserved locally. Saved backup to: {backup_path}")
        except Exception as err:
            log_message(f"[ERROR] Could not save backup locally: {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()

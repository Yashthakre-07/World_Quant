import sqlite3
import json
import os
import sys
import re
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add project root to path
from pathlib import Path
WQ_ROOT = Path("C:/Users/Admin/Documents/VIBE_YT/wq")
sys.path.insert(0, str(WQ_ROOT))

from src.registry import AlphaRegistry
from src.validator import validate_fastexpr

db_path = WQ_ROOT / "db" / "alpha_vault.db"

if not db_path.exists():
    print(f"Error: Database not found at {db_path}")
    sys.exit(1)

print(f"Connecting to local database: {db_path.name}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query all rows in alpha_runs where status = 'ERROR'
cursor.execute("SELECT formula, family, hypothesis, neutralization, decay, truncation, universe FROM alpha_runs WHERE status='ERROR';")
error_rows = cursor.fetchall()
print(f"Found {len(error_rows)} failed alphas (status = 'ERROR') in local database.")

fixed_alphas = []
for idx, (formula, family, hypothesis, neutralization, decay, truncation, universe) in enumerate(error_rows, 1):
    if not formula:
        continue
        
    original_formula = formula
    
    # --- FIX 1: Strip restricted pasteurize operator ---
    if "pasteurize" in formula:
        formula = re.sub(r'pasteurize\((.*?)\)', r'\1', formula)
        print(f"  [Fix pasteurize] #{idx}: '{original_formula}' -> '{formula}'")
        
    # --- FIX 2: Replace disallowed python comparisons 'and', 'or', 'not' ---
    if re.search(r'\b(and|or|not)\b', formula, re.IGNORECASE):
        formula = re.sub(r'\band\b', '&&', formula, flags=re.IGNORECASE)
        formula = re.sub(r'\bor\b', '||', formula, flags=re.IGNORECASE)
        formula = re.sub(r'\bnot\b', '!', formula, flags=re.IGNORECASE)
        print(f"  [Fix logical words] #{idx}: '{original_formula}' -> '{formula}'")

    # --- FIX 3: Check logical brackets and operators ---
    # (General rate limit 429 errors don't need changes, they just need to be run again safely!)

    alpha_obj = {
        "name": f"G_fixed_{idx:03d}",
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": universe or "TOP3000",
            "delay": 1,
            "decay": decay or 5,
            "neutralization": neutralization or "SUBINDUSTRY",
            "truncation": truncation or 0.08,
            "pasteurization": "ON",
            "testPeriod": "P0Y0M0D",
            "unitHandling": "VERIFY",
            "nanHandling": "OFF",
            "language": "FASTEXPR",
            "visualization": False,
        },
        "regular": formula,
        "dataset": "analyst10" if "analyst10" in family.lower() else "custom",
        "hypothesis": hypothesis or f"Restored and corrected WQ alpha from original run, index {idx}."
    }
    
    # Verify syntax before accepting
    is_valid, err_msg = validate_fastexpr(formula)
    if is_valid:
        fixed_alphas.append(alpha_obj)
    else:
        # If it still fails, let's see if we can do basic bracket cleanup
        # For instance, if it's missing trailing bracket due to string formatting, etc.
        print(f"  [Validation Failed] #{idx}: '{formula}' | Error: {err_msg}")

conn.close()

print(f"\nSuccessfully cleaned and validated {len(fixed_alphas)} out of {len(error_rows)} failed alphas.")

if not fixed_alphas:
    print("[!] No alphas were successfully fixed. Exiting.")
    sys.exit(0)

# 3. Add to unified registry
print("\nRegistering and appending fixed alphas to registry...")
registry = AlphaRegistry()
added, skipped = registry.append_batch(fixed_alphas)
print(f"Registry Result: Added={added}, Skipped={skipped}")

# 4. Push to remote websites review box
print("\nPushing fixed alphas back to API review queues...")
URL_TOKENS = {
    "https://world-quant.onrender.com/api/queue-alpha": "yashthakreop",
    "https://world-quant-1.onrender.com/api/queue-alpha": "yashthakreop1"
}

push_payload = []
for idx, a in enumerate(fixed_alphas, 1):
    push_payload.append({
        "family": f"fixed_errors_group_{(idx-1)//20 + 1}",
        "hypothesis": a["hypothesis"],
        "formula": a["regular"],
        "settings": {
            "decay": a["settings"]["decay"],
            "neutralization": a["settings"]["neutralization"],
            "universe": a["settings"]["universe"],
            "truncation": a["settings"]["truncation"]
        }
    })
    
for url, token in URL_TOKENS.items():
    print(f"\nConnecting to: {url} ...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=push_payload, headers=headers, timeout=60, verify=False)
        if response.status_code == 200:
            res_data = response.json()
            print(f"[SUCCESS] Alphas successfully queued on {url}.")
            print(f"Server Response: Added={res_data.get('added', 0)}, Skipped={res_data.get('skipped', 0)}")
        else:
            print(f"[FAILED] Server {url} returned status code {response.status_code}")
            print(f"Server Response: {response.text[:500]}")
    except Exception as e:
        print(f"[ERROR] Could not connect to {url}: {e}")

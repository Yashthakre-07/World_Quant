import sys
import json
import argparse
import requests
from pathlib import Path

# Load environment variables to read secret tokens and settings
sys.path.append(str(Path(__file__).resolve().parent))
try:
    from src.config import WQ_EMAIL
except ImportError:
    WQ_EMAIL = "unknown"

# 1. Default Configuration
DEFAULT_API_TOKEN = "wq-default-token-change-me"
DEFAULT_CONSOLE_URL = "http://127.0.0.1:8000/api/queue-alpha"

# 2. Template Generator
def generate_combinatorial_alphas(field_id, category_name):
    """Generates systematic combinatorial formulas for a given dataset field."""
    lookbacks = [2, 3, 5, 10, 15, 20, 22, 40]
    groups = ["industry", "subindustry"]
    formulas = []

    for d in lookbacks:
        # Volatility-Adjusted Momentum
        formulas.append(f"ts_delta({field_id}, {d})")
        formulas.append(f"ts_decay_linear(ts_delta({field_id}, {d}), {d})")
        formulas.append(f"rank(ts_delta({field_id}, {d}))")
        formulas.append(f"ts_rank(ts_delta({field_id}, {d}), {d})")
        formulas.append(f"ts_delta({field_id}, {d}) / (ts_std_dev({field_id}, {d}) + 0.001)")
        
        # Mean Reversion / Deviation
        formulas.append(f"-({field_id} - ts_mean({field_id}, {d}))")
        formulas.append(f"-rank({field_id} - ts_mean({field_id}, {d}))")
        formulas.append(f"-ts_decay_linear({field_id} - ts_mean({field_id}, {d}), {d})")
        formulas.append(f"-({field_id} - ts_mean({field_id}, {d})) / (ts_std_dev({field_id}, {d}) + 0.001)")
        formulas.append(f"-({field_id} - ts_min({field_id}, {d})) / (ts_max({field_id}, {d}) - ts_min({field_id}, {d}) + 0.0001)")

        # Group/Sector Neutralization
        for g in groups:
            formulas.append(f"group_zscore({field_id}, {g})")
            formulas.append(f"group_neutralize(ts_decay_linear(rank({field_id}), {d}), {g})")
            formulas.append(f"group_neutralize(ts_delta({field_id}, {d}), {g})")
            formulas.append(f"group_zscore(ts_delta(group_zscore({field_id}, {g}), {d}), {g})")

        # Price-Volume & Returns interactions
        formulas.append(f"{field_id} * returns")
        formulas.append(f"ts_corr(rank({field_id}), rank(returns), {d})")
        formulas.append(f"ts_delta({field_id}, {d}) / (ts_mean(volume, {d}) + 0.0001)")
        formulas.append(f"rank({field_id}) / (cap + 0.0001)")
        formulas.append(f"sign(ts_delta({field_id}, {d})) * returns")

    # Filter unique values and limit to 200
    unique = list(set(formulas))[:200]
    
    # Format as API payload queue items
    payload = []
    for idx, formula in enumerate(unique):
        payload.append({
            "formula": formula,
            "family": f"{category_name}_gen",
            "hypothesis": f"Systematic combinatorial factor research on field {field_id} (Lookback={d} days).",
            "settings": {
                "region": "USA",
                "universe": "TOP3000",
                "decay": 6,
                "neutralization": "SUBINDUSTRY"
            }
        })
    return payload

# 3. Main Runner CLI
def main():
    parser = argparse.ArgumentParser(description="AlphaForge - Systematic Combinatorial Trigger and Secure Queue Injector")
    parser.add_argument("--field", type=str, required=True, help="The target WorldQuant dataset field ID (e.g. analyst_rating_consensus)")
    parser.add_argument("--category", type=str, default="analyst_estimates", help="Category name for tagging the alpha family")
    parser.add_argument("--token", type=str, default=DEFAULT_API_TOKEN, help="Bearer token matching the API_SECRET_TOKEN set in console environment")
    parser.add_argument("--url", type=str, default=DEFAULT_CONSOLE_URL, help="The URL to the running console server push endpoint")
    
    args = parser.parse_args()
    
    print(f"[*] Target Field: {args.field}")
    print(f"[*] Category: {args.category}")
    print(f"[*] Generating combinatorial formula candidates...")
    
    payload = generate_combinatorial_alphas(args.field, args.category)
    print(f"[+] Successfully generated {len(payload)} unique alpha candidates.")
    
    # Send via secure HTTP POST
    print(f"[*] Pushing candidates to review inbox at: {args.url}...")
    headers = {
        "Authorization": f"Bearer {args.token}",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.post(args.url, json=payload, headers=headers, timeout=15)
        if r.status_code == 200:
            res = r.json()
            print(f"[SUCCESS] Pushed successfully!")
            print(f"          - Added to Review Box: {res.get('added_count', 0)}")
            print(f"          - Skipped (Duplicates): {res.get('skipped_count', 0)}")
            print(f"[INFO] Open the dashboard at http://127.0.0.1:8000 and check the 'Review Inbox' box to inject them into the active backtester!")
        else:
            print(f"[ERROR] API returned status {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[ERROR] Failed to connect to console server: {e}")

if __name__ == "__main__":
    main()

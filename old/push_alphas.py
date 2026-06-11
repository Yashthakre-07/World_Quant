# -*- coding: utf-8 -*-
"""
push_alphas.py
----------------
Unified, extensible pushing script that reads from the centralized 
alphas registry (registry.json), validates formulas locally, and 
securely queues them on live Render dashboards using bearer tokens.

Usage:
    python push_alphas.py --dataset analyst14
    python push_alphas.py --all
"""

import json
import os
import sys
import argparse
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add project root to path so we can import src.validator and src.registry
from pathlib import Path
WQ_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(WQ_ROOT))

from src.validator import validate_fastexpr
from src.registry import AlphaRegistry

def main():
    parser = argparse.ArgumentParser(description="AlphaForge - Extensible Secure Alphas Pusher")
    parser.add_argument("--dataset", type=str, default=None, help="Filter to push only a specific dataset (e.g. analyst14, analyst10)")
    parser.add_argument("--all", action="store_true", help="Push all alphas in the registry")
    args = parser.parse_args()

    # If neither argument is specified, default to pushing all
    target_dataset = args.dataset
    if not target_dataset and not args.all:
        print("[!] No target specified. Defaulting to all registered alphas.")
        args.all = True

    # 1. Load registry
    registry = AlphaRegistry()
    if not registry.alphas:
        print("[ERROR] Alpha registry is empty! Please generate alphas first.")
        sys.exit(1)

    # 2. Filter alphas if dataset is specified
    selected_alphas = []
    for a in registry.alphas:
        # Check dataset tag
        ds = a.get("dataset", "")
        if target_dataset and ds.lower() != target_dataset.lower():
            continue
        selected_alphas.append(a)

    print(f"\n[*] Filtered {len(selected_alphas)} alphas for dataset '{target_dataset or 'ALL'}' (Out of {len(registry.alphas)} total registered).")

    if not selected_alphas:
        print("[!] No matching alphas to push. Exiting.")
        sys.exit(0)

    # 3. Validate syntax of all selected alphas
    print("\n[*] Running local syntax validation check...")
    invalid_count = 0
    payload = []
    
    for idx, a in enumerate(selected_alphas, 1):
        formula = a.get("regular", a.get("formula"))
        is_valid, err_msg = validate_fastexpr(formula)
        if not is_valid:
            print(f"  [-] Invalid Alpha #{idx}: {formula} | Error: {err_msg}")
            invalid_count += 1
            continue
            
        settings = a.get("settings", {})
        mapped_settings = {
            "decay": settings.get("decay", 5),
            "neutralization": settings.get("neutralization", "SUBINDUSTRY"),
            "universe": settings.get("universe", "TOP3000"),
            "truncation": settings.get("truncation", 0.08)
        }
        
        payload.append({
            "family": f"{a.get('dataset', 'custom')}_group_{(idx-1)//20 + 1}",
            "hypothesis": a.get("hypothesis", f"Systematic quantitatively-researched alpha for {a.get('dataset', 'custom')}."),
            "formula": formula,
            "settings": mapped_settings
        })

    if invalid_count > 0:
        print(f"[WARNING] {invalid_count} alphas failed local validation and were skipped.")
    print(f"[+] Prepared {len(payload)} validated alphas for queuing.")

    # 4. Push payload to dashboards
    URL_TOKENS = {
        "http://127.0.0.1:8000/api/queue-alpha": "yashthakreop",
        "https://world-quant.onrender.com/api/queue-alpha": "yashthakreop",
        "https://world-quant-1.onrender.com/api/queue-alpha": "yashthakreop1"
    }
    
    for url, token in URL_TOKENS.items():
        print(f"\nConnecting to: {url} ...")
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            response = requests.post(url, json=payload, headers=headers, timeout=60, verify=False)
            if response.status_code == 200:
                res_data = response.json()
                print(f"[SUCCESS] Alphas successfully queued on {url}.")
                print(f"Server Response: Added={res_data.get('added', 0)}, Skipped={res_data.get('skipped', 0)}")
            else:
                print(f"[FAILED] Server {url} returned status code {response.status_code}")
                print(f"Server Response: {response.text[:500]}")
        except Exception as e:
            print(f"[ERROR] Could not connect to {url}: {e}")

    print("\nDone!")

if __name__ == "__main__":
    main()

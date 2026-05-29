# -*- coding: utf-8 -*-
"""
push_analyst14_alphas.py
----------------------------
Pushes the 200 newly generated and validated analyst14 alphas to the website's 
queue-alpha API review box with SSL bypass and server-specific authorization tokens.
"""

import json
import os
import sys
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WQ_ROOT = r"C:\Users\Admin\Documents\VIBE_YT\wq"

# Load the generated analyst14 alphas
alphas_file = os.path.join(WQ_ROOT, "alphas_dataset", "analyst14", "alphas", "generated_alphas.json")
if not os.path.exists(alphas_file):
    print(f"ERROR: Alphas file not found at {alphas_file}")
    sys.exit(1)

with open(alphas_file, "r", encoding="utf-8") as f:
    alphas = json.load(f)

print(f"[*] Loaded {len(alphas)} analyst14 alphas for pushing.")

URL_TOKENS = {
    "http://127.0.0.1:8000/api/queue-alpha": "yashthakreop",
    "https://world-quant.onrender.com/api/queue-alpha": "yashthakreop",
    "https://world-quant-1.onrender.com/api/queue-alpha": "yashthakreop1"
}
URLS = list(URL_TOKENS.keys())

# Map into API review inbox payload format
payload = []
for idx, a in enumerate(alphas, 1):
    formula = a["regular"]
    settings = a["settings"]
    
    # Map the settings
    mapped_settings = {
        "decay": settings.get("decay", 5),
        "neutralization": settings.get("neutralization", "SUBINDUSTRY"),
        "universe": settings.get("universe", "TOP3000"),
        "truncation": settings.get("truncation", 0.08)
    }
    
    payload.append({
        "family": f"analyst14_group_{(idx-1)//20 + 1}",
        "hypothesis": f"Systematic consensus, dispersion, neglect, and profitability ratio research on analyst14 dataset, group {(idx-1)//20 + 1}",
        "formula": formula,
        "settings": mapped_settings
    })

print(f"[*] Prepared {len(payload)} alphas for pushing to website review box.")

for url in URLS:
    print(f"\nConnecting to: {url} ...")
    try:
        token = URL_TOKENS[url]
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

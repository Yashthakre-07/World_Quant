import os
import json
import time
import requests
import re

# Config paths
yash_env_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\yash.env"
theme_json_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\theme_Dataset.json"
output_dir = r"c:\Users\Admin\Documents\VIBE_YT\wq\scratch\selected_analyst_fields"
os.makedirs(output_dir, exist_ok=True)

BRAIN_API = "https://api.worldquantbrain.com"

# 1. Parse WQ credentials from yash.env
email = None
password = None
if os.path.exists(yash_env_path):
    with open(yash_env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                if key.strip() == 'WQ_EMAIL':
                    email = val.strip()
                elif key.strip() == 'WQ_PASSWORD':
                    password = val.strip()

print(f"Credentials loaded: email={email}")

if not email or not password:
    print("[ERROR] WQ Credentials not found in yash.env!")
    exit(1)

# 2. Authenticate
s = requests.Session()
s.auth = (email, password)
r = s.post(f"{BRAIN_API}/authentication")
print(f"[AUTH] Status code: {r.status_code}")
if r.status_code != 201:
    print(f"[AUTH FAILED] {r.text[:200]}")
    exit(1)
print("[AUTH SUCCESS] Successfully authenticated with WorldQuant Brain.")

# 3. Load theme datasets
with open(theme_json_path, 'r', encoding='utf-8') as f:
    theme_datasets = json.load(f)

# 4. Determine which ones are missing locally
missing_datasets = []
for ds in theme_datasets:
    ds_id = ds['id']
    target_path = os.path.join(output_dir, f"{ds_id}_fields.json")
    # If file doesn't exist or is empty, we consider it missing
    if not os.path.exists(target_path) or os.path.getsize(target_path) < 10:
        missing_datasets.append(ds)

print(f"Found {len(missing_datasets)} datasets missing local field JSON files out of {len(theme_datasets)} total.")

# 5. Fetch fields for each missing dataset
INSTRUMENT_TYPE = "EQUITY"
REGION          = "USA"
DELAY           = 1
UNIVERSE        = "TOP3000"

def fetch_fields(ds_id):
    all_fields = []
    offset = 0
    limit = 50
    total = None
    
    while True:
        url = (
            f"{BRAIN_API}/data-fields"
            f"?instrumentType={INSTRUMENT_TYPE}"
            f"&region={REGION}"
            f"&delay={DELAY}"
            f"&universe={UNIVERSE}"
            f"&dataset.id={ds_id}"
            f"&limit={limit}"
            f"&offset={offset}"
        )
        r = s.get(url)
        if r.status_code == 429:
            print("      [RATE LIMIT] Waiting 10s...")
            time.sleep(10)
            continue
        if r.status_code == 401:
            print("      [UNAUTHORIZED] Re-authenticating...")
            s.post(f"{BRAIN_API}/authentication")
            continue
        if r.status_code != 200:
            print(f"      [ERROR] {r.status_code}: {r.text[:200]}")
            break
            
        data = r.json()
        results = data.get("results", [])
        if total is None:
            total = data.get("count", 0)
            
        all_fields.extend(results)
        offset += len(results)
        
        if not results or (total is not None and offset >= total):
            break
            
        time.sleep(0.2)
        
    return all_fields, total

# Start downloading
for idx, ds in enumerate(missing_datasets, 1):
    ds_id = ds['id']
    ds_name = ds['name']
    print(f"[{idx}/{len(missing_datasets)}] Downloading fields for {ds_id} ({ds_name})...")
    
    fields, total = fetch_fields(ds_id)
    print(f"    Fetched {len(fields)} fields (expected count from API: {total})")
    
    # Save to JSON
    out_path = os.path.join(output_dir, f"{ds_id}_fields.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(fields, f, indent=2)
    print(f"    Saved to {os.path.basename(out_path)}")
    time.sleep(0.5)

print("\nAll downloads finished!")

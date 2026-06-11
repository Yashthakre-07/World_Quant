"""
fetch_analyst_fields_via_ace.py
================================
Uses ACE API (WorldQuant Brain official API) to fetch ALL datafields
for analyst10, analyst14, and analyst15 datasets directly from Brain.
Saves results as JSON files for use in alpha generation.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
import json
import time
import requests
from pathlib import Path

# ── CONFIG ──────────────────────────────────────────────────────────────────
BRAIN_API = "https://api.worldquantbrain.com"
CREDENTIALS_PATH = os.path.join(os.path.expanduser("~"), "secrets", "platform-brain.json")
OUTPUT_DIR = Path(r"C:\Users\Admin\Documents\VIBE_YT\wq\scratch\analyst_fields")
OUTPUT_DIR.mkdir(exist_ok=True)

# Target datasets
TARGET_DATASETS = ["analyst10", "analyst14", "analyst15"]

# Simulation config to filter fields
INSTRUMENT_TYPE = "EQUITY"
REGION          = "USA"
DELAY           = 1
UNIVERSE        = "TOP3000"

# ── AUTH ─────────────────────────────────────────────────────────────────────
def get_session():
    with open(CREDENTIALS_PATH) as f:
        creds = json.load(f)
    
    s = requests.Session()
    s.auth = (creds["email"], creds["password"])
    
    print(f"[AUTH] Authenticating as {creds['email']}...")
    r = s.post(f"{BRAIN_API}/authentication")
    
    if r.status_code == 201:
        print(f"[AUTH] SUCCESS - Authenticated!")
        return s
    elif r.status_code == 401:
        # Check for biometric
        if "WWW-Authenticate" in r.headers and r.headers["WWW-Authenticate"] == "persona":
            biometric_url = r.headers.get("Location", "")
            if "api.worldquantbrain.com" in biometric_url:
                biometric_url = biometric_url.replace("api.worldquantbrain.com", "platform.worldquantbrain.com")
            print(f"\n[AUTH] Biometric authentication required!")
            print(f"  Please visit: {biometric_url}")
            input("  Press ENTER after completing biometric auth...")
            r2 = s.post(f"{BRAIN_API}/authentication")
            if r2.status_code == 201:
                print("[AUTH] SUCCESS after biometric!")
                return s
            else:
                print(f"[AUTH] FAILED after biometric: {r2.status_code} {r2.text[:200]}")
                sys.exit(1)
        else:
            print(f"[AUTH] FAILED: {r.status_code} {r.text[:200]}")
            sys.exit(1)
    else:
        print(f"[AUTH] Status: {r.status_code} - continuing...")
        return s

# ── FETCH FIELDS ─────────────────────────────────────────────────────────────
def fetch_all_fields_for_dataset(s, dataset_id):
    """Fetch ALL fields for a specific dataset using pagination."""
    print(f"\n[FETCH] Getting fields for dataset: {dataset_id}")
    
    all_fields = []
    offset = 0
    limit = 50   # WQ Brain max seems lower - start at 50, fallback below
    total = None
    
    while True:
        url = (
            f"{BRAIN_API}/data-fields"
            f"?instrumentType={INSTRUMENT_TYPE}"
            f"&region={REGION}"
            f"&delay={DELAY}"
            f"&universe={UNIVERSE}"
            f"&dataset.id={dataset_id}"
            f"&limit={limit}"
            f"&offset={offset}"
        )
        
        r = s.get(url)
        
        if r.status_code == 429:
            print(f"  [RATE LIMIT] Waiting 15s...")
            time.sleep(15)
            continue
        
        if r.status_code == 400 and "limit" in r.text.lower():
            # Reduce limit and retry
            limit = limit // 2
            if limit < 5:
                print(f"  [ERROR] Cannot find working limit. Trying search approach...")
                break
            print(f"  [LIMIT] Reducing limit to {limit} and retrying...")
            continue
        
        if r.status_code != 200:
            print(f"  [ERROR] HTTP {r.status_code}: {r.text[:200]}")
            break
        
        data = r.json()
        results = data.get("results", [])
        
        if total is None:
            total = data.get("count", 0)
            print(f"  Total fields available: {total}")
        
        if not results:
            break
        
        all_fields.extend(results)
        offset += len(results)
        
        print(f"  Fetched {len(all_fields)}/{total} fields...", end="\r")
        
        # If we have all of them, stop
        if len(all_fields) >= total or len(results) < limit:
            break
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    print(f"\n  DONE: {len(all_fields)} fields fetched for {dataset_id}")
    return all_fields

def fetch_dataset_info(s, dataset_id):
    """Get dataset metadata."""
    url = (
        f"{BRAIN_API}/data-sets"
        f"?instrumentType={INSTRUMENT_TYPE}"
        f"&region={REGION}"
        f"&delay={DELAY}"
        f"&universe={UNIVERSE}"
        f"&id={dataset_id}"
    )
    r = s.get(url)
    if r.status_code == 200:
        results = r.json().get("results", [])
        return results[0] if results else {}
    return {}

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    s = get_session()
    
    all_results = {}
    
    for ds_id in TARGET_DATASETS:
        print(f"\n{'='*60}")
        print(f"DATASET: {ds_id}")
        print(f"{'='*60}")
        
        # Get dataset info
        info = fetch_dataset_info(s, ds_id)
        if info:
            print(f"  Name       : {info.get('name', 'N/A')}")
            print(f"  Description: {info.get('description', 'N/A')[:100]}")
            print(f"  Category   : {info.get('category', 'N/A')}")
        
        # Fetch all fields
        fields = fetch_all_fields_for_dataset(s, ds_id)
        all_results[ds_id] = fields
        
        # Save individual file
        out_path = OUTPUT_DIR / f"{ds_id}_fields.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(fields, f, indent=2, ensure_ascii=False)
        print(f"  Saved -> {out_path}")
        
        # Print summary of field IDs
        print(f"\n  FIELD IDs (first 20):")
        for field in fields[:20]:
            fid = field.get("id", "N/A")
            fname = field.get("name", "N/A")
            ftype = field.get("type", "N/A")
            print(f"    {fid:55s} | {ftype:15s} | {fname}")
        
        if len(fields) > 20:
            print(f"    ... and {len(fields) - 20} more (see {out_path})")
        
        # Small pause between datasets
        time.sleep(1)
    
    # Save combined file
    combined_path = OUTPUT_DIR / "all_analyst_fields_combined.json"
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n{'='*60}")
    print(f"COMBINED FILE saved -> {combined_path}")
    
    # Print final summary
    print(f"\n=== FINAL SUMMARY ===")
    for ds_id, fields in all_results.items():
        print(f"  {ds_id}: {len(fields)} fields")
    
    print("\n[SUCCESS] All analyst fields downloaded from WQ Brain ACE API!")

if __name__ == "__main__":
    main()

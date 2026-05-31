"""
fetch_all_available_fields_sai.py
===================================
Uses SAI's WQ Brain account to fetch ALL available datasets and fields.
Sai's account is the one licensed for analyst10/14/15.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os, json, time, requests
from pathlib import Path

BRAIN_API = "https://api.worldquantbrain.com"
OUTPUT_DIR = Path(r"C:\Users\Admin\Documents\VIBE_YT\wq\scratch\analyst_fields_sai")
OUTPUT_DIR.mkdir(exist_ok=True)

# SAI's credentials directly
SAI_EMAIL    = "saineela731@gmail.com"
SAI_PASSWORD = "iitg@123"

INSTRUMENT_TYPE = "EQUITY"
REGION          = "USA"
DELAY           = 1
UNIVERSE        = "TOP3000"

# ── AUTH ──────────────────────────────────────────────────────────────────
s = requests.Session()
s.auth = (SAI_EMAIL, SAI_PASSWORD)
print(f"[AUTH] Authenticating as {SAI_EMAIL}...")
r = s.post(f"{BRAIN_API}/authentication")
print(f"[AUTH] Status: {r.status_code}")

if r.status_code == 401:
    if "WWW-Authenticate" in r.headers and r.headers["WWW-Authenticate"] == "persona":
        loc = r.headers.get("Location", "")
        if "api.worldquantbrain.com" in loc:
            loc = loc.replace("api.worldquantbrain.com", "platform.worldquantbrain.com")
        print(f"\n[AUTH] Biometric required! Visit:\n  {loc}")
        input("  Press ENTER after completing biometric auth...")
        r2 = s.post(f"{BRAIN_API}/authentication")
        if r2.status_code == 201:
            print("[AUTH] SUCCESS after biometric!")
        else:
            print(f"[AUTH] FAILED: {r2.status_code} {r2.text[:200]}")
            sys.exit(1)
    else:
        print(f"[AUTH] FAILED: wrong password? {r.text[:200]}")
        sys.exit(1)
elif r.status_code != 201:
    print(f"[AUTH] Unexpected: {r.status_code} - continuing anyway...")

# ── STEP 1: Get ALL available datasets ────────────────────────────────────
print("\n=== STEP 1: All available datasets for SAI's account ===")
all_datasets = []
offset = 0

while True:
    url = (
        f"{BRAIN_API}/data-sets"
        f"?instrumentType={INSTRUMENT_TYPE}&region={REGION}"
        f"&delay={DELAY}&universe={UNIVERSE}&limit=20&offset={offset}"
    )
    r = s.get(url)
    if r.status_code == 429:
        print("  [RATE LIMIT] Waiting 15s...")
        time.sleep(15)
        continue
    if r.status_code != 200:
        print(f"  [ERROR] {r.status_code}: {r.text[:200]}")
        break
    data = r.json()
    results = data.get("results", [])
    total = data.get("count", 0)
    all_datasets.extend(results)
    offset += len(results)
    if not results or offset >= total:
        break
    time.sleep(0.5)

print(f"Found {len(all_datasets)} datasets:")
analyst_datasets = []
for ds in all_datasets:
    ds_id = ds.get("id", "?")
    ds_name = ds.get("name", "?")
    print(f"  [{ds_id:35s}] {ds_name}")
    if "analyst" in ds_id.lower():
        analyst_datasets.append(ds_id)

print(f"\nAnalyst datasets: {analyst_datasets}")

with open(OUTPUT_DIR / "available_datasets.json", "w", encoding="utf-8") as f:
    json.dump(all_datasets, f, indent=2, ensure_ascii=False)

# ── STEP 2: Fetch fields for each analyst dataset ─────────────────────────
print("\n=== STEP 2: Fetching fields for each analyst dataset ===")

def fetch_fields(s, dataset_id, limit=20):
    all_fields = []
    offset = 0
    total = None
    while True:
        url = (
            f"{BRAIN_API}/data-fields"
            f"?instrumentType={INSTRUMENT_TYPE}&region={REGION}"
            f"&delay={DELAY}&universe={UNIVERSE}"
            f"&dataset.id={dataset_id}&limit={limit}&offset={offset}"
        )
        r = s.get(url)
        if r.status_code == 429:
            print(f"    [RATE LIMIT] Waiting 15s...")
            time.sleep(15)
            continue
        if r.status_code == 400:
            if limit > 5:
                limit = limit // 2
                print(f"    [LIMIT] Trying limit={limit}...")
                continue
            print(f"    [ERROR 400]: {r.text[:100]}")
            break
        if r.status_code != 200:
            print(f"    [ERROR {r.status_code}]: {r.text[:100]}")
            break
        data = r.json()
        results = data.get("results", [])
        if total is None:
            total = data.get("count", 0)
        all_fields.extend(results)
        offset += len(results)
        print(f"    {len(all_fields)}/{total}", end="\r")
        if not results or offset >= total:
            break
        time.sleep(0.3)
    return all_fields, total or 0

# Fetch for all analyst datasets found
TARGET_DATASETS = analyst_datasets if analyst_datasets else ["analyst4", "analyst10", "analyst14", "analyst15"]

all_results = {}
for ds_id in TARGET_DATASETS:
    print(f"\n  --- {ds_id} ---")
    fields, total = fetch_fields(s, ds_id)
    print(f"  Got {len(fields)}/{total} fields")
    all_results[ds_id] = fields

    out_path = OUTPUT_DIR / f"{ds_id}_fields.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fields, f, indent=2, ensure_ascii=False)

    if fields:
        types = {}
        for field in fields:
            t = field.get("type", "?")
            types[t] = types.get(t, 0) + 1
        print(f"  Types: {types}")
        print(f"  First 15 field IDs:")
        for field in fields[:15]:
            fid = field.get("id", "N/A")
            ftype = field.get("type", "N/A")
            print(f"    {fid:55s} | {ftype}")
    time.sleep(1)

# ── STEP 3: Search by key prefixes ────────────────────────────────────────
print("\n=== STEP 3: Search for fields by analyst prefix ===")
time.sleep(2)  # avoid rate limit

for prefix in ["anl4_", "anl10_", "anl14_", "anl15_"]:
    url = (
        f"{BRAIN_API}/data-fields"
        f"?instrumentType={INSTRUMENT_TYPE}&region={REGION}"
        f"&delay={DELAY}&universe={UNIVERSE}"
        f"&search={prefix}&limit=20&offset=0"
    )
    r = s.get(url)
    if r.status_code == 429:
        time.sleep(15)
        r = s.get(url)
    if r.status_code == 200:
        data = r.json()
        count = data.get("count", 0)
        results = data.get("results", [])
        print(f"\n  search='{prefix}' -> TOTAL COUNT = {count}")
        for field in results[:8]:
            fid = field.get("id", "?")
            ftype = field.get("type", "?")
            print(f"    {fid:55s} | {ftype}")
    else:
        print(f"\n  search='{prefix}' -> HTTP {r.status_code}: {r.text[:100]}")
    time.sleep(1.5)

# ── STEP 4: Full download of all accessible analyst fields ────────────────
print("\n=== STEP 4: Full paginated download of all accessible fields ===")
time.sleep(2)

grand_fields = {}
for prefix in ["anl4_", "anl10_", "anl14_", "anl15_"]:
    fetched = []
    offset = 0
    limit = 20
    total = None
    
    while True:
        url = (
            f"{BRAIN_API}/data-fields"
            f"?instrumentType={INSTRUMENT_TYPE}&region={REGION}"
            f"&delay={DELAY}&universe={UNIVERSE}"
            f"&search={prefix}&limit={limit}&offset={offset}"
        )
        r = s.get(url)
        if r.status_code == 429:
            time.sleep(15)
            continue
        if r.status_code != 200:
            break
        data = r.json()
        results = data.get("results", [])
        if total is None:
            total = data.get("count", 0)
        fetched.extend(results)
        offset += len(results)
        print(f"  {prefix}: {len(fetched)}/{total}", end="\r")
        if not results or offset >= total:
            break
        time.sleep(0.4)
    
    print(f"\n  {prefix}: {len(fetched)} fields total")
    grand_fields[prefix] = fetched
    
    out_path = OUTPUT_DIR / f"fields_{prefix.rstrip('_')}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fetched, f, indent=2, ensure_ascii=False)
    
    # Separate VECTOR vs MATRIX
    vectors  = [f for f in fetched if f.get("type") == "VECTOR"]
    matrices = [f for f in fetched if f.get("type") == "MATRIX"]
    print(f"    VECTOR={len(vectors)}, MATRIX={len(matrices)}")
    
    time.sleep(1)

# Save combined
with open(OUTPUT_DIR / "all_fields_combined.json", "w", encoding="utf-8") as f:
    json.dump(grand_fields, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print("FINAL SUMMARY (SAI's account):")
for prefix, fields in grand_fields.items():
    vectors  = [f for f in fields if f.get("type") == "VECTOR"]
    matrices = [f for f in fields if f.get("type") == "MATRIX"]
    print(f"  {prefix:12s}: {len(fields):5d} fields | VECTOR={len(vectors)} | MATRIX={len(matrices)}")

print(f"\nAll files saved to: {OUTPUT_DIR}")
print("=== DONE ===")

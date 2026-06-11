"""
fetch_all_available_fields.py
==============================
1. Fetches ALL available datasets for this WQ Brain account
2. Identifies which analyst datasets are accessible
3. Downloads ALL fields from every accessible dataset with pagination
4. Saves to JSON for alpha generation
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os, json, time, requests
from pathlib import Path

BRAIN_API = "https://api.worldquantbrain.com"
CREDENTIALS_PATH = os.path.join(os.path.expanduser("~"), "secrets", "platform-brain.json")
OUTPUT_DIR = Path(r"C:\Users\Admin\Documents\VIBE_YT\wq\scratch\analyst_fields")
OUTPUT_DIR.mkdir(exist_ok=True)

INSTRUMENT_TYPE = "EQUITY"
REGION          = "USA"
DELAY           = 1
UNIVERSE        = "TOP3000"

# ── AUTH ──────────────────────────────────────────────────────────────────
with open(CREDENTIALS_PATH) as f:
    creds = json.load(f)

s = requests.Session()
s.auth = (creds["email"], creds["password"])
r = s.post(f"{BRAIN_API}/authentication")
print(f"[AUTH] {r.status_code} - {'SUCCESS' if r.status_code == 201 else 'FAILED'}")
if r.status_code != 201:
    print(f"  {r.text[:200]}")
    sys.exit(1)

# ── STEP 1: Get ALL available datasets ────────────────────────────────────
print("\n=== STEP 1: Fetching ALL available datasets ===")
all_datasets = []
offset = 0
limit = 20

while True:
    url = (
        f"{BRAIN_API}/data-sets"
        f"?instrumentType={INSTRUMENT_TYPE}"
        f"&region={REGION}"
        f"&delay={DELAY}"
        f"&universe={UNIVERSE}"
        f"&limit={limit}&offset={offset}"
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

print(f"\nTotal datasets available: {len(all_datasets)}")
print("\nAll datasets:")
for ds in all_datasets:
    ds_id = ds.get("id", "?")
    ds_name = ds.get("name", "?")
    ds_desc = ds.get("description", "?")[:80]
    print(f"  [{ds_id:30s}] {ds_name}")

# Save dataset list
with open(OUTPUT_DIR / "available_datasets.json", "w", encoding="utf-8") as f:
    json.dump(all_datasets, f, indent=2, ensure_ascii=False)

# ── STEP 2: Download fields for EACH dataset ──────────────────────────────
print("\n=== STEP 2: Downloading fields for each dataset ===")

def fetch_fields_paginated(s, dataset_id, limit=20):
    """Fetch all fields for a dataset with proper pagination."""
    all_fields = []
    offset = 0
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
            print(f"    [RATE LIMIT] Waiting 15s...")
            time.sleep(15)
            continue
        if r.status_code == 400:
            # Try lower limit
            if limit > 5:
                limit = limit // 2
                print(f"    [LIMIT FIX] Reducing limit to {limit}...")
                continue
            print(f"    [ERROR] HTTP 400: {r.text[:100]}")
            break
        if r.status_code != 200:
            print(f"    [ERROR] HTTP {r.status_code}: {r.text[:100]}")
            break

        data = r.json()
        results = data.get("results", [])
        if total is None:
            total = data.get("count", 0)

        all_fields.extend(results)
        offset += len(results)

        if not results or (total is not None and offset >= total):
            break

        time.sleep(0.3)

    return all_fields, total or 0

all_fields_by_dataset = {}

for ds in all_datasets:
    ds_id = ds.get("id", "?")
    ds_name = ds.get("name", "?")
    
    print(f"\n  Dataset: {ds_id} ({ds_name})")
    fields, expected_total = fetch_fields_paginated(s, ds_id)
    
    print(f"    Fetched {len(fields)} / {expected_total} fields")
    all_fields_by_dataset[ds_id] = fields
    
    # Save individual file
    out_path = OUTPUT_DIR / f"{ds_id}_fields.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fields, f, indent=2, ensure_ascii=False)
    
    # Print first 10 field IDs
    if fields:
        for field in fields[:10]:
            fid = field.get("id", "N/A")
            ftype = field.get("type", "N/A")
            fdesc = field.get("description", field.get("name", ""))[:50]
            print(f"      {fid:55s} | {ftype:10s} | {fdesc}")
        if len(fields) > 10:
            print(f"      ... +{len(fields)-10} more")
    
    time.sleep(1)

# ── STEP 3: Search for analyst fields by prefix ────────────────────────────
print("\n=== STEP 3: Searching fields by dataset prefix ===")

# The key insight: analyst4 uses 'anl4_' prefix
# Let's do targeted searches for specific analyst types
analyst_searches = [
    ("analyst4", "anl4_"),
    ("analyst4_analyst10", "anl10_"),
    ("analyst4_analyst14", "anl14_"),
    ("analyst4_analyst15", "anl15_"),
]

print("\n  Searching for fields by ID prefix...")
for search_name, prefix in analyst_searches:
    url = (
        f"{BRAIN_API}/data-fields"
        f"?instrumentType={INSTRUMENT_TYPE}"
        f"&region={REGION}"
        f"&delay={DELAY}"
        f"&universe={UNIVERSE}"
        f"&search={prefix}"
        f"&limit=20&offset=0"
    )
    r = s.get(url)
    if r.status_code == 429:
        time.sleep(15)
        r = s.get(url)
    
    if r.status_code == 200:
        data = r.json()
        count = data.get("count", 0)
        results = data.get("results", [])
        print(f"\n  prefix='{prefix}' -> count={count}")
        for field in results[:5]:
            print(f"    {field.get('id','?'):55s} | {field.get('type','?')}")
    else:
        print(f"\n  prefix='{prefix}' -> HTTP {r.status_code}: {r.text[:100]}")
    time.sleep(1)

# ── STEP 4: Full paginated fetch of anl4_ fields ─────────────────────────
print("\n=== STEP 4: Full paginated fetch of ALL anl4_ fields ===")
all_anl4_fields = []
offset = 0
limit = 20
total = None

while True:
    url = (
        f"{BRAIN_API}/data-fields"
        f"?instrumentType={INSTRUMENT_TYPE}"
        f"&region={REGION}"
        f"&delay={DELAY}"
        f"&universe={UNIVERSE}"
        f"&search=anl4_"
        f"&limit={limit}&offset={offset}"
    )
    r = s.get(url)
    
    if r.status_code == 429:
        print("  [RATE LIMIT] Waiting 15s...")
        time.sleep(15)
        continue
    if r.status_code != 200:
        print(f"  [ERROR] {r.status_code}: {r.text[:100]}")
        break
    
    data = r.json()
    results = data.get("results", [])
    if total is None:
        total = data.get("count", 0)
        print(f"  Total anl4_ fields available: {total}")
    
    all_anl4_fields.extend(results)
    offset += len(results)
    
    print(f"  Progress: {len(all_anl4_fields)}/{total}", end="\r")
    
    if not results or offset >= total:
        break
    
    time.sleep(0.4)

print(f"\n  DONE: {len(all_anl4_fields)} anl4_ fields fetched")

# Save anl4 fields
with open(OUTPUT_DIR / "anl4_all_fields.json", "w", encoding="utf-8") as f:
    json.dump(all_anl4_fields, f, indent=2, ensure_ascii=False)

# Print by type
types = {}
for f in all_anl4_fields:
    t = f.get("type", "?")
    types[t] = types.get(t, 0) + 1
print(f"  By type: {types}")

# Separate VECTOR (daily) vs MATRIX (event-driven)
vectors = [f for f in all_anl4_fields if f.get("type") == "VECTOR"]
matrices = [f for f in all_anl4_fields if f.get("type") == "MATRIX"]
print(f"  VECTOR (daily, safe for ts_* ops): {len(vectors)}")
print(f"  MATRIX (event-driven, restricted): {len(matrices)}")

with open(OUTPUT_DIR / "anl4_VECTOR_fields.json", "w", encoding="utf-8") as f:
    json.dump(vectors, f, indent=2, ensure_ascii=False)
with open(OUTPUT_DIR / "anl4_MATRIX_fields.json", "w", encoding="utf-8") as f:
    json.dump(matrices, f, indent=2, ensure_ascii=False)

print("\n  VECTOR field IDs (safe for ts_decay_linear, ts_mean etc.):")
for field in vectors[:20]:
    print(f"    {field.get('id','?')}")

print("\n  MATRIX field IDs (event-driven - only rank/ratio allowed):")
for field in matrices[:20]:
    print(f"    {field.get('id','?')}")

print(f"\n{'='*60}")
print("FILES SAVED:")
print(f"  {OUTPUT_DIR}/available_datasets.json")
print(f"  {OUTPUT_DIR}/anl4_all_fields.json")
print(f"  {OUTPUT_DIR}/anl4_VECTOR_fields.json")
print(f"  {OUTPUT_DIR}/anl4_MATRIX_fields.json")
print("=== DONE ===")

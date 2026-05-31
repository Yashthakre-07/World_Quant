"""
fetch_fields_sai_cookies.py
============================
Uses Sai's already-saved session cookies to fetch ALL analyst fields
directly from WQ Brain API — no biometric required!
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json, time, requests
from pathlib import Path

BRAIN_API   = "https://api.worldquantbrain.com"
COOKIES_PATH = Path(r"C:\Users\Admin\Documents\VIBE_YT\wq\db\session_cookies_saineela731_gmail_com.json")
OUTPUT_DIR   = Path(r"C:\Users\Admin\Documents\VIBE_YT\wq\scratch\analyst_fields_sai")
OUTPUT_DIR.mkdir(exist_ok=True)

INSTRUMENT_TYPE = "EQUITY"
REGION          = "USA"
DELAY           = 1
UNIVERSE        = "TOP3000"

# ── Load cookies & build session ──────────────────────────────────────────
with open(COOKIES_PATH, "r") as f:
    cookies = json.load(f)

s = requests.Session()
s.cookies.update(cookies)
s.verify = False
requests.packages.urllib3.disable_warnings()

# Verify session is valid
print("[AUTH] Verifying Sai's session cookies...")
r = s.get(f"{BRAIN_API}/users/self", timeout=15)
print(f"[AUTH] Status: {r.status_code}")
if r.status_code == 200:
    user = r.json()
    print(f"[AUTH] Logged in as: {user.get('email', user.get('username', 'Sai'))}")
    print(f"[AUTH] Name: {user.get('firstName','?')} {user.get('lastName','?')}")
elif r.status_code == 401:
    print("[AUTH] Session expired! Please login to local server first to refresh cookies.")
    print("       Start server: python run_pipeline.py")
    print("       Login at:     http://localhost:5000")
    sys.exit(1)
else:
    print(f"[AUTH] Warning: HTTP {r.status_code} — trying anyway...")

# ── STEP 1: Get ALL datasets available to Sai ─────────────────────────────
print("\n=== STEP 1: All available datasets for Sai's account ===")
all_datasets = []
offset = 0
while True:
    url = (f"{BRAIN_API}/data-sets?instrumentType={INSTRUMENT_TYPE}"
           f"&region={REGION}&delay={DELAY}&universe={UNIVERSE}&limit=20&offset={offset}")
    r = s.get(url, timeout=20)
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

print(f"\nTotal datasets: {len(all_datasets)}")
analyst_datasets = []
for ds in all_datasets:
    ds_id = ds.get("id","?")
    ds_name = ds.get("name","?")
    print(f"  [{ds_id:35s}] {ds_name}")
    if "analyst" in ds_id.lower():
        analyst_datasets.append(ds_id)

with open(OUTPUT_DIR / "available_datasets.json", "w", encoding="utf-8") as f:
    json.dump(all_datasets, f, indent=2, ensure_ascii=False)
print(f"\nAnalyst datasets found: {analyst_datasets}")

# ── STEP 2: Fetch fields for all analyst datasets ─────────────────────────
print("\n=== STEP 2: Downloading fields per dataset ===")

def fetch_fields_for_dataset(s, ds_id, limit=20):
    all_fields = []
    offset = 0
    total = None
    while True:
        url = (f"{BRAIN_API}/data-fields?instrumentType={INSTRUMENT_TYPE}"
               f"&region={REGION}&delay={DELAY}&universe={UNIVERSE}"
               f"&dataset.id={ds_id}&limit={limit}&offset={offset}")
        r = s.get(url, timeout=20)
        if r.status_code == 429:
            time.sleep(15); continue
        if r.status_code == 400:
            if limit > 5:
                limit //= 2
                print(f"    Reducing limit to {limit}...")
                continue
            break
        if r.status_code != 200:
            print(f"    ERROR {r.status_code}: {r.text[:100]}")
            break
        data = r.json()
        results = data.get("results", [])
        if total is None:
            total = data.get("count", 0)
        all_fields.extend(results)
        offset += len(results)
        print(f"    {ds_id}: {len(all_fields)}/{total}", end="\r")
        if not results or offset >= total:
            break
        time.sleep(0.3)
    return all_fields, total or 0

# Fetch for all detected analyst datasets + try explicit ones
target_datasets = list(set(analyst_datasets + ["analyst4","analyst10","analyst14","analyst15","analyst25","analyst7"]))

all_fields_map = {}
for ds_id in target_datasets:
    fields, total = fetch_fields_for_dataset(s, ds_id)
    print(f"\n  {ds_id}: {len(fields)}/{total} fields")
    if fields:
        all_fields_map[ds_id] = fields
        out_path = OUTPUT_DIR / f"{ds_id}_fields.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(fields, f, indent=2, ensure_ascii=False)
        # Type breakdown
        types = {}
        for field in fields:
            t = field.get("type","?")
            types[t] = types.get(t,0) + 1
        print(f"    Types: {types}")
        print(f"    First 10 IDs:")
        for field in fields[:10]:
            print(f"      {field.get('id','?'):55s} | {field.get('type','?')}")
    time.sleep(1)

# ── STEP 3: Search by prefix for ALL analyst field variants ───────────────
print("\n=== STEP 3: Search by prefix across all fields ===")
time.sleep(2)

grand_download = {}
for prefix in ["anl4_", "anl10_", "anl14_", "anl15_", "anl7_", "anl25_"]:
    fetched = []
    offset  = 0
    limit   = 20
    total   = None
    while True:
        url = (f"{BRAIN_API}/data-fields?instrumentType={INSTRUMENT_TYPE}"
               f"&region={REGION}&delay={DELAY}&universe={UNIVERSE}"
               f"&search={prefix}&limit={limit}&offset={offset}")
        r = s.get(url, timeout=20)
        if r.status_code == 429:
            time.sleep(15); continue
        if r.status_code != 200:
            print(f"  {prefix} -> HTTP {r.status_code}")
            break
        data = r.json()
        results = data.get("results",[])
        if total is None:
            total = data.get("count", 0)
            print(f"\n  prefix='{prefix}': TOTAL = {total}")
        fetched.extend(results)
        offset += len(results)
        print(f"    Fetched {len(fetched)}/{total}", end="\r")
        if not results or offset >= total:
            break
        time.sleep(0.35)

    print(f"\n  '{prefix}': {len(fetched)} fields")
    grand_download[prefix] = fetched

    if fetched:
        out_path = OUTPUT_DIR / f"fields_{prefix.rstrip('_')}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(fetched, f, indent=2, ensure_ascii=False)
        vectors  = [f for f in fetched if f.get("type") == "VECTOR"]
        matrices = [f for f in fetched if f.get("type") == "MATRIX"]
        print(f"    VECTOR (safe for ts_* ops): {len(vectors)}")
        print(f"    MATRIX (event-driven):      {len(matrices)}")
        print(f"    Sample IDs:")
        for field in fetched[:10]:
            print(f"      {field.get('id','?'):55s} | {field.get('type','?')}")
    time.sleep(1)

# ── SAVE combined ─────────────────────────────────────────────────────────
with open(OUTPUT_DIR / "grand_combined.json", "w", encoding="utf-8") as f:
    json.dump(grand_download, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print("FINAL SUMMARY — SAI's WQ Brain Account:")
for prefix, fields in grand_download.items():
    if fields:
        vectors  = len([f for f in fields if f.get("type") == "VECTOR"])
        matrices = len([f for f in fields if f.get("type") == "MATRIX"])
        print(f"  {prefix:10s}: {len(fields):5d} fields | VECTOR={vectors} | MATRIX={matrices}")
    else:
        print(f"  {prefix:10s}: 0 fields (NOT ACCESSIBLE)")

print(f"\nFiles saved to: {OUTPUT_DIR}")
print("=== DONE ===")

"""
download_selected_analyst_datasets.py
======================================
Uses Sai's validated session to download specific fields for user-defined analyst datasets.
"""
import sys, io, json, time, requests
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BRAIN_API   = "https://api.worldquantbrain.com"
COOKIES_PATH = Path(r"C:\Users\Admin\Documents\VIBE_YT\wq\db\session_cookies_saineela731_gmail_com.json")
OUTPUT_DIR   = Path(r"C:\Users\Admin\Documents\VIBE_YT\wq\scratch\selected_analyst_fields")
OUTPUT_DIR.mkdir(exist_ok=True)

INSTRUMENT_TYPE = "EQUITY"
REGION          = "USA"
DELAY           = 1
UNIVERSE        = "TOP3000"

# Target datasets selected by the user
TARGET_DATASETS = [
    "analyst10", "analyst14", "analyst15", "analyst25", "analyst4", 
    "analyst45", "analyst48", "analyst49", "analyst69", "analyst7", 
    "analyst8", "analyst82", "analyst83", "analyst94", 
    "analyst_base_ref", "analyst_consensus", "analyst_factor_signals", 
    "biasfree_analyst", "model211", "other423"
]

# Load cookies & build session
with open(COOKIES_PATH, "r") as f:
    cookies = json.load(f)

s = requests.Session()
s.cookies.update(cookies)
s.verify = False
requests.packages.urllib3.disable_warnings()

# Verify session
print("[AUTH] Verifying Sai's session cookies...")
r = s.get(f"{BRAIN_API}/users/self", timeout=15)
if r.status_code != 200:
    print(f"[AUTH] Expired or invalid session: {r.status_code}")
    sys.exit(1)
print(f"[AUTH] Logged in successfully!")

def fetch_fields_for_dataset(s, ds_id, limit=50):
    all_fields = []
    offset = 0
    total = None
    retry_count = 0
    
    while True:
        url = (f"{BRAIN_API}/data-fields?instrumentType={INSTRUMENT_TYPE}"
               f"&region={REGION}&delay={DELAY}&universe={UNIVERSE}"
               f"&dataset.id={ds_id}&limit={limit}&offset={offset}")
        try:
            r = s.get(url, timeout=20)
            if r.status_code == 429:
                print(f"\n    [RATE LIMIT] Spaced on {ds_id} (offset {offset}). Waiting 15s...")
                time.sleep(15)
                continue
            if r.status_code == 400:
                if limit > 10:
                    limit //= 2
                    print(f"\n    [WARNING] Reducing chunk limit to {limit}...")
                    continue
                break
            if r.status_code != 200:
                print(f"\n    [ERROR] {r.status_code} fetching {ds_id}")
                break
            
            data = r.json()
            results = data.get("results", [])
            if total is None:
                total = data.get("count", 0)
                print(f"  * Dataset [{ds_id}]: Total fields = {total}")
                if total == 0:
                    break
            
            all_fields.extend(results)
            offset += len(results)
            print(f"    Fetched: {len(all_fields)}/{total}", end="\r")
            
            if not results or offset >= total:
                break
            time.sleep(0.3)
            retry_count = 0
        except Exception as ex:
            retry_count += 1
            if retry_count > 3:
                print(f"\n    [ERROR] Failed repeatedly on {ds_id} offset {offset}: {ex}")
                break
            print(f"\n    [TIMEOUT/CONN] Retrying in 10s... ({retry_count}/3)")
            time.sleep(10)
            
    return all_fields, total or 0

print("\n=== STARTING TARGETED FIELDS DOWNLOAD ===")
download_summary = {}

for ds_id in TARGET_DATASETS:
    print(f"\nProcessing [{ds_id}]...")
    fields, total = fetch_fields_for_dataset(s, ds_id)
    if fields:
        out_path = OUTPUT_DIR / f"{ds_id}_fields.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(fields, f, indent=2, ensure_ascii=False)
        vectors  = len([f for f in fields if f.get("type") == "VECTOR"])
        matrices = len([f for f in fields if f.get("type") == "MATRIX"])
        download_summary[ds_id] = {"total": len(fields), "VECTOR": vectors, "MATRIX": matrices}
        print(f"\n    Saved {len(fields)} fields -> VECTOR={vectors}, MATRIX={matrices}")
    else:
        print(f"    No fields found or not accessible for {ds_id}.")
    time.sleep(1)

# Combined summary output
print(f"\n{'='*60}\nTARGETED DOWNLOAD COMPLETE SUMMARY:")
for ds, stats in download_summary.items():
    print(f"  {ds:25s}: Total={stats['total']:5d} | VECTOR={stats['VECTOR']:4d} | MATRIX={stats['MATRIX']:4d}")
print(f"\nData stored in: {OUTPUT_DIR}")
print("=== DONE ===")

"""
probe_ace_api.py
=================
Probe WQ Brain API to find correct parameters for fetching dataset fields.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os, json, time, requests
from pathlib import Path

BRAIN_API = "https://api.worldquantbrain.com"
CREDENTIALS_PATH = os.path.join(os.path.expanduser("~"), "secrets", "platform-brain.json")

with open(CREDENTIALS_PATH) as f:
    creds = json.load(f)

s = requests.Session()
s.auth = (creds["email"], creds["password"])
r = s.post(f"{BRAIN_API}/authentication")
print(f"[AUTH] {r.status_code}")

# ── PROBE 1: What limits does the API accept? ─────────────────────────────
print("\n=== PROBE 1: Test different limits ===")
for limit in [5, 10, 20, 50]:
    url = f"{BRAIN_API}/data-fields?instrumentType=EQUITY&region=USA&delay=1&universe=TOP3000&dataset.id=analyst10&limit={limit}&offset=0"
    r = s.get(url)
    print(f"  limit={limit} -> HTTP {r.status_code}", end="")
    if r.status_code == 200:
        data = r.json()
        print(f" | count={data.get('count','?')} | results={len(data.get('results',[]))}")
    else:
        print(f" | {r.text[:100]}")
    time.sleep(1)

# ── PROBE 2: Try without dataset filter ───────────────────────────────────
print("\n=== PROBE 2: No dataset filter, search='analyst10' ===")
url = f"{BRAIN_API}/data-fields?instrumentType=EQUITY&region=USA&delay=1&universe=TOP3000&search=analyst10&limit=20&offset=0"
r = s.get(url)
print(f"  HTTP {r.status_code}", end="")
if r.status_code == 200:
    data = r.json()
    print(f" | count={data.get('count','?')} | results={len(data.get('results',[]))}")
    for f in data.get("results", [])[:5]:
        print(f"    -> id={f.get('id')} | name={f.get('name','?')[:60]} | type={f.get('type','?')}")
else:
    print(f" | {r.text[:200]}")

# ── PROBE 3: Try dataset.id filter with small limit ────────────────────────
print("\n=== PROBE 3: dataset.id filter with limit=20 ===")
for ds in ["analyst10", "analyst14", "analyst15"]:
    url = f"{BRAIN_API}/data-fields?instrumentType=EQUITY&region=USA&delay=1&universe=TOP3000&dataset.id={ds}&limit=20&offset=0"
    r = s.get(url)
    print(f"  {ds} -> HTTP {r.status_code}", end="")
    if r.status_code == 200:
        data = r.json()
        print(f" | total_count={data.get('count','?')} | got={len(data.get('results',[]))}")
        for f in data.get("results", [])[:3]:
            print(f"    id={f.get('id')} | type={f.get('type','?')}")
    else:
        print(f" | {r.text[:150]}")
    time.sleep(1)

# ── PROBE 4: Check dataset endpoint ────────────────────────────────────────
print("\n=== PROBE 4: /data-sets endpoint ===")
url = f"{BRAIN_API}/data-sets?instrumentType=EQUITY&region=USA&delay=1&universe=TOP3000&limit=20&offset=0"
r = s.get(url)
print(f"  HTTP {r.status_code}", end="")
if r.status_code == 200:
    data = r.json()
    print(f" | count={data.get('count','?')}")
    for ds in data.get("results", []):
        ds_id = ds.get("id","?")
        if "analyst" in ds_id.lower():
            print(f"    FOUND: id={ds_id} | name={ds.get('name','?')}")
else:
    print(f" | {r.text[:200]}")

# ── PROBE 5: Try the /data-sets/{id}/data-fields endpoint ─────────────────
print("\n=== PROBE 5: /data-sets/{id} direct endpoint ===")
for ds in ["analyst10", "analyst14", "analyst15"]:
    url = f"{BRAIN_API}/data-sets/{ds}"
    r = s.get(url)
    print(f"  /data-sets/{ds} -> HTTP {r.status_code}")
    if r.status_code == 200:
        print(f"    {str(r.json())[:200]}")

# ── PROBE 6: Exact raw JSON structure of a working request ─────────────────
print("\n=== PROBE 6: Raw response structure ===")
url = f"{BRAIN_API}/data-fields?instrumentType=EQUITY&region=USA&delay=1&universe=TOP3000&dataset.id=analyst15&limit=10&offset=0"
r = s.get(url)
print(f"  HTTP {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"  Keys: {list(data.keys())}")
    print(f"  count: {data.get('count')}")
    results = data.get("results", [])
    if results:
        print(f"  First field keys: {list(results[0].keys())}")
        print(f"  First 5 fields:")
        for f in results[:5]:
            print(f"    {json.dumps(f, ensure_ascii=False)[:200]}")
else:
    print(f"  ERROR: {r.text[:300]}")

print("\n=== PROBE DONE ===")

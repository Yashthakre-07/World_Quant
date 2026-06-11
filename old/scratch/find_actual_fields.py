import json

with open("scratch/discovered_whitelists.json", "r", encoding="utf-8") as f:
    wl = json.load(f)

print("--- ANALYST4 FIELDS ---")
for k, v in wl.get("analyst4", {}).items():
    if isinstance(v, list):
        print(f"  {k} (len={len(v)}):")
        for x in v[:10]:
            print(f"    {x}")

print("\n--- SEARCHING FOR ROE, BVPS, EBITDA, NETINC, REVENUE ---")
for ds_id, data in wl.items():
    for f_type in ["vectors", "matrices"]:
        for f in data.get(f_type, []):
            f_lower = f.lower()
            if any(term in f_lower for term in ["ebitda", "bvps", "roe", "netinc", "revenue", "job_postings"]):
                print(f"[{ds_id}][{f_type}] {f}")

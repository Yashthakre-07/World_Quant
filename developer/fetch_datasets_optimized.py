import os
import json
import time
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load env from sai.env first, falling back to yash.env, then .env
for env_name in ["sai.env", "yash.env", ".env"]:
    env_path = Path(__file__).resolve().parent / env_name
    if env_path.exists():
        load_dotenv(env_path, override=True)
        break
else:
    load_dotenv()

from src.auth import WQSession

EMAIL = os.getenv("WQ_EMAIL")
PASSWORD = os.getenv("WQ_PASSWORD")
BASE_URL = "https://api.worldquantbrain.com"
OUT_DIR = Path("documentation/dataset")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FIELD_PARAMS = {
    "region": "USA",
    "delay": 1,
    "universe": "TOP3000",
    "instrumentType": "EQUITY",
    "limit": 50,
}

def get_session():
    return WQSession()

def get_json(s, url, params=None, retries=6):
    for attempt in range(retries):
        try:
            r = s.get(url, params=params, timeout=30)
            if r.status_code == 429:
                wait = 15 * (attempt + 1)
                print(f"\n  [rate-limit] sleeping {wait}s ...")
                time.sleep(wait)
                continue
            if r.status_code != 200:
                print(f"\n  [HTTP {r.status_code}] Error details: {r.text}")
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"\n  [warn] {e} -- retry {attempt+1}/{retries}")
            time.sleep(6)
    return None

def fetch_all_fields(s):
    print("[->] Fetching all fields from /data-fields paginated...")
    params = dict(FIELD_PARAMS)
    params["offset"] = 0
    all_fields = []
    
    while True:
        data = get_json(s, f"{BASE_URL}/data-fields", params)
        if data is None:
            break
        
        items = data.get("results", []) if isinstance(data, dict) else data
        total = data.get("count", 0) if isinstance(data, dict) else len(items)
        
        all_fields.extend(items)
        pct = round(len(all_fields) / max(total, 1) * 100)
        print(f"    ... Fields fetched: {len(all_fields)}/{total} ({pct}%)", end="\r", flush=True)
        
        if len(all_fields) >= total or not items:
            break
            
        params["offset"] += params["limit"]
        time.sleep(0.8) # Keep it gentle to avoid rate limit
        
    print()
    return all_fields

def build_catalog(s):
    # 1. Fetch datasets
    print("[->] Fetching all datasets ...")
    raw = get_json(s, f"{BASE_URL}/data-sets")
    if not raw:
        print("[ERR] No datasets returned.")
        return {}
    all_ds = raw.get("results", raw) if isinstance(raw, dict) else raw
    print(f"[OK] {len(all_ds)} datasets found")
    
    (OUT_DIR / "raw_datasets.json").write_text(
        json.dumps(all_ds, indent=2), encoding="utf-8"
    )
    
    # 2. Fetch all fields
    all_fields = fetch_all_fields(s)
    print(f"[OK] {len(all_fields)} total fields fetched")
    
    # Group fields by dataset ID
    fields_by_dataset = {}
    for f in all_fields:
        ds_info = f.get("dataset", {})
        ds_id = ds_info.get("id") if isinstance(ds_info, dict) else str(ds_info)
        if ds_id:
            fields_by_dataset.setdefault(ds_id, []).append(f)
            
    # Group datasets by category
    by_cat = {}
    for ds in all_ds:
        cat_obj = ds.get("category") or {}
        cat = cat_obj.get("name", "Uncategorized") if isinstance(cat_obj, dict) else str(cat_obj)
        by_cat.setdefault(cat, []).append(ds)
        
    catalog = {}
    for cat_name in sorted(by_cat.keys()):
        datasets = by_cat[cat_name]
        cat_entry = {"name": cat_name, "datasets": []}
        catalog[cat_name] = cat_entry
        
        for ds in datasets:
            ds_id = ds.get("id", "")
            ds_name = ds.get("name", ds_id)
            
            subcat_obj = ds.get("subcategory") or {}
            subcat = subcat_obj.get("name", "") if isinstance(subcat_obj, dict) else str(subcat_obj)
            
            ds_entry = {
                "id":            ds_id,
                "name":          ds_name,
                "description":   ds.get("description", ""),
                "category":      cat_name,
                "subcategory":   subcat,
                "region":        ds.get("region", "USA"),
                "delay":         ds.get("delay", ""),
                "universe":      ds.get("universe", ""),
                "dateCoverage":  ds.get("dateCoverage", ""),
                "coverage":      ds.get("coverage", ""),
                "valueScore":    ds.get("valueScore", ""),
                "fieldCount":    ds.get("fieldCount", ""),
                "userCount":     ds.get("userCount", ""),
                "alphaCount":    ds.get("alphaCount", ""),
                "researchPapers": ds.get("researchPapers", []),
                "fields":        [],
            }
            
            # Map fields
            ds_fields = fields_by_dataset.get(ds_id, [])
            for f in ds_fields:
                ds_entry["fields"].append({
                    "id":          f.get("id", ""),
                    "name":        f.get("id", ""),
                    "description": f.get("description", ""),
                    "type":        f.get("type", ""),
                    "coverage":    f.get("coverage", ""),
                    "alphaCount":  f.get("alphaCount", ""),
                    "dataset_id":  ds_id,
                    "dataset":     ds_name,
                    "category":    cat_name,
                })
                
            cat_entry["datasets"].append(ds_entry)
            
    return catalog

def save_all(catalog):
    print(f"\n{'='*60}")
    print("  Saving outputs to documentation/dataset/ ...")
    print(f"{'='*60}")

    # 1. Master JSON
    p = OUT_DIR / "all_datasets.json"
    p.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"[OK] Full JSON        -> {p}")

    # 2. Per-category JSON
    for cat_name, cat_data in catalog.items():
        safe = cat_name.lower().replace(" ", "_").replace("/", "_")
        p = OUT_DIR / f"category_{safe}.json"
        p.write_text(json.dumps(cat_data, indent=2), encoding="utf-8")
        total_f = sum(len(d["fields"]) for d in cat_data["datasets"])
        print(f"[OK] {cat_name:<20} -> {p}  ({total_f} fields)")

    # 3. Master Markdown
    lines = [
        "# WorldQuant Brain — Complete Dataset Catalog\n\n",
        "> Auto-generated via WQ Brain API  \n",
        "> Coverage: USA / TOP3000 / EQUITY / Delay-1\n\n",
        "---\n\n",
        "## Summary\n\n",
        "| Category | Datasets | Total Fields | Value Score |\n",
        "|----------|----------|-------------|-------------|\n",
    ]

    summary_rows = []
    for cat_name in sorted(catalog.keys()):
        cat_data = catalog[cat_name]
        n_ds  = len(cat_data["datasets"])
        n_fld = sum(len(d["fields"]) for d in cat_data["datasets"])
        vs    = cat_data["datasets"][0].get("valueScore", "?") if cat_data["datasets"] else "?"
        lines.append(f"| [{cat_name}](#{cat_name.lower().replace(' ', '-')}) | {n_ds} | {n_fld} | {vs} |\n")
        summary_rows.append((cat_name, cat_data, n_ds, n_fld))

    lines.append("\n---\n\n")

    for cat_name, cat_data, n_ds, n_fld in summary_rows:
        lines += [
            f"## {cat_name}\n\n",
            f"**Datasets:** {n_ds} | **Total Fields:** {n_fld} | **Region:** USA\n\n",
        ]
        for ds in cat_data["datasets"]:
            lines += [
                f"### `{ds['name']}`\n\n",
                f"**Dataset ID:** `{ds['id']}`  \n",
                f"**Description:** {ds.get('description') or 'N/A'}  \n",
                f"**Date Coverage:** {ds.get('dateCoverage', '?')} | ",
                f"**Value Score:** {ds.get('valueScore', '?')} | ",
                f"**Fields:** {len(ds['fields'])}  \n\n",
                "| Field ID | Description | Type |\n",
                "|----------|-------------|------|\n",
            ]
            for f in ds["fields"]:
                desc = (f.get("description") or "").replace("|", "\\|").replace("\n", " ")
                desc = (desc[:160] + "...") if len(desc) > 160 else desc
                lines.append(f"| `{f.get('id', '?')}` | {desc} | {f.get('type', '?')} |\n")
            if ds.get("researchPapers"):
                lines.append("\n**Research Papers:**\n")
                for rp in ds["researchPapers"]:
                    lines.append(f"- [{rp.get('title', 'Paper')}]({rp.get('url', '#')})\n")
            lines.append("\n---\n\n")

    p = OUT_DIR / "DATASET_CATALOG.md"
    p.write_text("".join(lines), encoding="utf-8")
    print(f"[OK] Markdown catalog -> {p}")

    # 4. Flat CSV
    csv_rows = ["category,dataset_id,dataset_name,field_id,description,type\n"]
    for cat_name in sorted(catalog.keys()):
        for ds in catalog[cat_name]["datasets"]:
            for f in ds["fields"]:
                desc = (f.get("description") or "").replace('"', '""').replace("\n", " ")
                csv_rows.append(
                    f'"{cat_name}","{ds["id"]}","{ds["name"]}","{f.get("id","")}","{desc}","{f.get("type","")}"\n'
                )
    p = OUT_DIR / "fields_index.csv"
    p.write_text("".join(csv_rows), encoding="utf-8")
    print(f"[OK] Fields CSV       -> {p}")

    # 5. Stats JSON
    total_fields = sum(
        len(ds["fields"])
        for cat in catalog.values()
        for ds in cat["datasets"]
    )
    stats = {
        "categories": len(catalog),
        "total_datasets": sum(len(c["datasets"]) for c in catalog.values()),
        "total_fields": total_fields,
        "by_category": {
            cn: {"datasets": nd, "fields": nf}
            for cn, _, nd, nf in summary_rows
        },
    }
    p = OUT_DIR / "catalog_stats.json"
    p.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(f"[OK] Stats            -> {p}")
    return stats

if __name__ == "__main__":
    print("=" * 60)
    print("  WorldQuant Brain - Dataset Catalog Fetcher (Optimized)")
    print("=" * 60)

    session = get_session()
    catalog = build_catalog(session)

    if not catalog:
        print("[ERR] No data collected.")
        sys.exit(1)

    stats = save_all(catalog)

    print(f"\n{'='*60}")
    print(f"  DONE!")
    print(f"  Categories : {stats['categories']}")
    print(f"  Datasets   : {stats['total_datasets']}")
    print(f"  Fields     : {stats['total_fields']}")
    print(f"  Output dir : documentation/dataset/")
    print(f"{'='*60}")

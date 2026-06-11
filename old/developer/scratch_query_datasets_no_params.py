import json
import time
import sys
from src.auth import WQSession

# Set stdout encoding to utf-8 just in case
sys.stdout.reconfigure(encoding='utf-8')

def get_json_with_retry(session, url, retries=6):
    for attempt in range(retries):
        try:
            r = session.get(url, timeout=30)
            if r.status_code == 429:
                wait = 15 * (attempt + 1)
                print(f"  [rate-limit] sleeping {wait}s ...")
                time.sleep(wait)
                continue
            if r.status_code != 200:
                print(f"  [HTTP {r.status_code}] Error: {r.text}")
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"  [warn] {e} -- retry {attempt+1}/{retries}")
            time.sleep(5)
    return None

def main():
    session = WQSession()
    url = "https://api.worldquantbrain.com/data-sets"
    print("Fetching all datasets in one go (no params)...")
    res = get_json_with_retry(session, url)
    if res:
        results = res.get("results", []) if isinstance(res, dict) else res
        print(f"Total records fetched: {len(results)}")
        
        # Save the full raw results to a file first
        with open("documentation/dataset/all_raw_datasets_unfiltered.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print("Full unfiltered raw datasets saved to documentation/dataset/all_raw_datasets_unfiltered.json")
        
        # Group by Category -> Subcategory -> Dataset ID -> Dataset Name
        hierarchy = {}
        for ds in results:
            cat_name = ds.get("category", {}).get("name", "Uncategorized").strip()
            subcat_name = ds.get("subcategory", {}).get("name", "N/A").strip()
            ds_id = ds["id"].strip()
            ds_name = ds["name"].strip()
            
            if cat_name not in hierarchy:
                hierarchy[cat_name] = {}
            if subcat_name not in hierarchy[cat_name]:
                hierarchy[cat_name][subcat_name] = {}
            hierarchy[cat_name][subcat_name][ds_id] = ds_name
            
        print("\n=== Unique Dataset Summary ===")
        for cat in sorted(hierarchy.keys()):
            cat_ds_count = sum(len(hierarchy[cat][sc]) for sc in hierarchy[cat])
            print(f"Category: {cat} ({cat_ds_count} unique datasets)")
            for subcat in sorted(hierarchy[cat].keys()):
                print(f"  Subcategory: {subcat}")
                for ds_id, ds_name in sorted(hierarchy[cat][subcat].items()):
                    print(f"    - [{ds_id}]: {ds_name}")

if __name__ == "__main__":
    main()

import json
import time
from src.auth import WQSession

def main():
    session = WQSession()
    
    url = "https://api.worldquantbrain.com/data-sets"
    params = {"limit": 50, "offset": 0}
    
    unique_datasets = {}
    total_records = 0
    
    print("Fetching all datasets via paginated API calls (limit=50)...")
    while True:
        try:
            r = session.get(url, params=params, timeout=30)
            if r.status_code != 200:
                print(f"Error: {r.status_code} - {r.text}")
                break
                
            res = r.json()
            results = res.get("results", [])
            if not results:
                break
                
            total_records += len(results)
            print(f"  Fetched {total_records} / {res.get('count')} records...")
            
            # Filter for Analyst datasets
            for d in results:
                cat_obj = d.get("category") or {}
                is_analyst = False
                if isinstance(cat_obj, dict):
                    if cat_obj.get("name") == "Analyst" or cat_obj.get("id") == "analyst":
                        is_analyst = True
                elif isinstance(cat_obj, str):
                    if cat_obj.lower() == "analyst":
                        is_analyst = True
                        
                if is_analyst:
                    ds_id = d.get("id")
                    if ds_id not in unique_datasets:
                        unique_datasets[ds_id] = {
                            "name": d.get("name"),
                            "description": d.get("description", "No description"),
                            "regions": set(),
                            "universes": set()
                        }
                    unique_datasets[ds_id]["regions"].add(d.get("region"))
                    unique_datasets[ds_id]["universes"].add(d.get("universe"))
            
            # Increment offset
            params["offset"] += len(results)
            if params["offset"] >= res.get("count", 0):
                break
                
            time.sleep(0.1) # Sleep briefly to be nice to the API
        except Exception as e:
            print(f"Error during pagination loop: {e}")
            break
            
    print(f"\nFound {len(unique_datasets)} unique Analyst datasets:")
    for idx, (ds_id, info) in enumerate(sorted(unique_datasets.items())):
        print(f"  [{idx+1}] ID: {ds_id} | Name: {info['name']}")
        print(f"      Regions: {list(info['regions'])}")
        print(f"      Universes (sample): {list(info['universes'])[:5]}")
        desc = info['description']
        desc_snippet = desc[:100] + "..." if len(desc) > 100 else desc
        print(f"      Description: {desc_snippet}")

if __name__ == "__main__":
    main()

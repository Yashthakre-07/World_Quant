import json
import os
from pathlib import Path
from src.auth import WQSession

def main():
    # Authenticate session using WQSession
    session = WQSession()
    
    # 1. Query raw dataset metadata for 'analyst4' from local JSON to see its structure
    try:
        with open("documentation/dataset/raw_datasets.json", "r") as f:
            raw_datasets = json.load(f)
        print(f"Total raw datasets in cache: {len(raw_datasets)}")
        analyst_ds = [d for d in raw_datasets if "analyst" in d.get("id", "")]
        if analyst_ds:
            print("\nKeys in local cached dataset object:")
            print(list(analyst_ds[0].keys()))
            print("\nSample local cached Analyst dataset object:")
            print(json.dumps(analyst_ds[0], indent=2))
    except Exception as e:
        print(f"Failed to read local cache: {e}")

    # 2. Query WorldQuant Brain API for analyst4 dataset detail to see live subscription status
    print("\nQuerying WorldQuant Brain API for 'analyst4' dataset detail...")
    try:
        url = "https://api.worldquantbrain.com/data-sets/analyst4"
        r = session.get(url, timeout=30)
        if r.status_code == 200:
            res_json = r.json()
            print("Successfully retrieved dataset info from API:")
            print(json.dumps(res_json, indent=2))
            
            # Check user subscription status
            # Sometimes subscription is indicated in a key like 'subscription' or 'active' or similar
            sub_status = res_json.get("subscription", None)
            print(f"\nSubscription field: {sub_status}")
        else:
            print(f"Failed to query API: HTTP {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Error querying API: {e}")

if __name__ == "__main__":
    main()

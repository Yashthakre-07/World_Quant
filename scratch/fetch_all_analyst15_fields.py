import json
import os
import sys
import pandas as pd
from pathlib import Path

# Add ace_api_extracted folder to path so we can import ace_lib
ACE_LIB_DIR = r"C:\Users\Admin\Documents\VIBE_YT\wq\documentation\ace_api_extracted"
sys.path.insert(0, ACE_LIB_DIR)

import ace_lib

print("Starting session with active credentials...")
try:
    s = ace_lib.start_session()
    print("Session established successfully!")
    
    all_fields = []
    limit = 50
    offset = 0
    
    while True:
        print(f"Fetching fields with offset={offset}...")
        url = f"https://api.worldquantbrain.com/data-fields?instrumentType=EQUITY&region=USA&delay=1&universe=TOP3000&limit={limit}&offset={offset}&search=analyst15"
        r = s.get(url)
        if r.status_code != 200:
            print(f"Error fetching URL: status={r.status_code}, response={r.text}")
            break
            
        data = r.json()
        results = data.get("results", [])
        if not results:
            print("No more results found.")
            break
            
        all_fields.extend(results)
        print(f"Fetched {len(results)} fields. Cumulative: {len(all_fields)}")
        
        if len(results) < limit:
            print("Reached last page.")
            break
            
        offset += limit
        
    print(f"\nSuccessfully fetched {len(all_fields)} total fields for analyst15!")
    
    # Save the fields to the alphas_dataset folder
    out_fields_path = r"C:\Users\Admin\Documents\VIBE_YT\wq\alphas_dataset\analyst15\alphas\fields.json"
    os.makedirs(os.path.dirname(out_fields_path), exist_ok=True)
    
    with open(out_fields_path, "w", encoding="utf-8") as f:
        json.dump(all_fields, f, indent=2)
    print(f"Saved all {len(all_fields)} fields to {out_fields_path}")
    
    # Also save to scratch for backup
    scratch_path = r"C:\Users\Admin\Documents\VIBE_YT\wq\scratch\analyst15_fields_all.json"
    with open(scratch_path, "w", encoding="utf-8") as f:
        json.dump(all_fields, f, indent=2)
        
    # Print a summary of categories/fields
    df = pd.DataFrame(all_fields)
    print("\nSummary of fields:")
    if "id" in df.columns:
        for idx, row in df.head(40).iterrows():
            print(f"  {row['id']} - {row.get('description', '')[:60]}")
    
except Exception as e:
    print(f"Error during execution: {e}")

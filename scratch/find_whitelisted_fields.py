import json
import os

files = {
    "analyst4": "scratch/selected_analyst_fields/analyst4_fields.json",
    "analyst14": "scratch/selected_analyst_fields/analyst14_fields.json",
    "analyst45": "scratch/selected_analyst_fields/analyst45_fields.json",
}

for name, filepath in files.items():
    if os.path.exists(filepath):
        print(f"\n==========================================")
        print(f"VALID FIELD NAMES IN {name.upper()}")
        print(f"==========================================")
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Search for exact IDs matching common quantitative fields
        matching = []
        for item in data:
            fid = item.get('id', '')
            desc = item.get('description', '')
            
            # Look for eps, sales, ptp, ebitda, fcf, alpha, relative_return
            keywords = ["eps", "sales", "ptp", "ebitda", "fcf", "alpha", "relative_return", "recommendation", "recommend", "analyst"]
            if any(k in fid.lower() or k in desc.lower() for k in keywords):
                matching.append(f"  - {fid} | {desc}")
                
        print(f"Found {len(matching)} matching fields. Sample fields:")
        for m in matching[:25]:
            print(m)

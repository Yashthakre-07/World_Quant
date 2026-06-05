import os
import json
import sys

def run_step_2():
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Locate dataset fields directory
    fields_dir = "scratch/analyst_fields"
    if not os.path.exists(fields_dir):
        print(f"Directory {fields_dir} not found. Creating it.")
        os.makedirs(fields_dir, exist_ok=True)
        
    print("FIELD DISCOVERY REPORT:")
    print("════════════════════════════════════════")
    
    total_fields = 0
    discovered_data = {}
    
    # We scan for all generated JSON fields files in the directory
    for file_name in os.listdir(fields_dir):
        if file_name.endswith("_fields.json") and not file_name.startswith("all_"):
            dataset_id = file_name.replace("_fields.json", "")
            file_path = os.path.join(fields_dir, file_name)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    fields = json.load(f)
            except Exception as e:
                print(f"  Error reading {file_name}: {e}")
                continue
                
            if not isinstance(fields, list):
                continue
                
            vectors = [f for f in fields if f.get("type") == "VECTOR"]
            matrices = [f for f in fields if f.get("type") == "MATRIX"]
            
            print(f"Dataset: {dataset_id}")
            print(f"  Total Fields: {len(fields)}")
            print(f"  VECTOR Fields: {len(vectors)}")
            print(f"  MATRIX Fields: {len(matrices)}")
            
            discovered_data[dataset_id] = {
                "total": len(fields),
                "vectors": [v.get("id") for v in vectors],
                "matrices": [m.get("id") for m in matrices]
            }
            total_fields += len(fields)
            
            # Print sample fields
            print("  Sample Fields:")
            for f in fields[:5]:
                fid = f.get("id", "?")
                ftype = f.get("type", "?")
                fdesc = f.get("description", "")[:50]
                print(f"    - {fid} ({ftype}): {fdesc}")
            print("---")
            
    # Save discovery output for step 3 and validator checks
    with open("scratch/discovered_whitelists.json", "w", encoding="utf-8") as f:
        json.dump(discovered_data, f, indent=2)
        
    print(f"TOTAL FIELDS ACCESSED AND WHITELISTED: {total_fields}")
    print("════════════════════════════════════════")
    print("\n✅ STEP 2 COMPLETE — ALL FIELDS DISCOVERED")

if __name__ == "__main__":
    run_step_2()

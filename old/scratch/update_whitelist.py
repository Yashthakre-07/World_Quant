import os
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    fields_dir = "scratch/selected_analyst_fields"
    whitelist_path = "scratch/discovered_whitelists.json"
    
    # Load existing whitelist if it exists
    if os.path.exists(whitelist_path):
        with open(whitelist_path, "r", encoding="utf-8") as f:
            whitelist = json.load(f)
    else:
        whitelist = {}
        
    print(f"Loaded existing whitelist with {len(whitelist)} datasets.")
    
    # Scan selected_analyst_fields directory
    for file_name in os.listdir(fields_dir):
        if file_name.endswith("_fields.json") and not file_name.startswith("all_"):
            dataset_id = file_name.replace("_fields.json", "")
            file_path = os.path.join(fields_dir, file_name)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    fields = json.load(f)
            except Exception as e:
                print(f"Error reading {file_name}: {e}")
                continue
                
            if not isinstance(fields, list):
                continue
                
            vectors = [f.get("id") for f in fields if f.get("type") == "VECTOR"]
            matrices = [f.get("id") for f in fields if f.get("type") == "MATRIX"]
            
            # Merge or overwrite in whitelist
            whitelist[dataset_id] = {
                "total": len(fields),
                "vectors": vectors,
                "matrices": matrices
            }
            print(f"Added/Updated dataset {dataset_id}: {len(fields)} fields ({len(vectors)} vectors, {len(matrices)} matrices).")
            
    # Save back to whitelist
    with open(whitelist_path, "w", encoding="utf-8") as f:
        json.dump(whitelist, f, indent=2)
        
    print("Whitelist successfully updated.")

if __name__ == "__main__":
    main()

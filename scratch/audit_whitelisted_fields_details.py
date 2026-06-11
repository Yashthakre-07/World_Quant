import csv
import json
import os
import re
from pathlib import Path

def audit():
    base_dir = Path(__file__).resolve().parent.parent
    
    # Storage maps
    datasets_fields = {} # dataset_id -> {'vectors': set(), 'matrices': set()}
    
    # 1. Load from fields_index.csv
    csv_path = base_dir / "documentation" / "dataset" / "fields_index.csv"
    if csv_path.exists():
        try:
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # skip header
                for row in reader:
                    if len(row) >= 6:
                        cat = row[0].strip()
                        ds_id = row[1].strip()
                        field_id = row[3].strip()
                        field_type = row[5].strip() # VECTOR or MATRIX
                        
                        if ds_id not in datasets_fields:
                            datasets_fields[ds_id] = {'vectors': set(), 'matrices': set()}
                        
                        if field_type == 'VECTOR':
                            datasets_fields[ds_id]['vectors'].add(field_id)
                        else:
                            datasets_fields[ds_id]['matrices'].add(field_id)
        except Exception as e:
            print("Error reading CSV:", e)
            
    # 2. Load from alphas_dataset/
    alphas_dataset_dir = base_dir / "alphas_dataset"
    if alphas_dataset_dir.exists():
        try:
            for p in alphas_dataset_dir.glob("**/fields.json"):
                # Get dataset id from parent folder name
                ds_id = p.parent.name
                if ds_id not in datasets_fields:
                    datasets_fields[ds_id] = {'vectors': set(), 'matrices': set()}
                
                with open(p, "r", encoding="utf-8") as f:
                    fields_data = json.load(f)
                    for item in fields_data:
                        if isinstance(item, dict) and "id" in item:
                            fid = item["id"]
                            # Default logic to classify: if it contains consensus/actual, it is vector
                            # or check if it starts with 'anl' and ends with '_estimate' etc.
                            # Standard WQ: analyst consensus vectors are usually sparse
                            is_vector = False
                            if "estimate" in fid.lower() or "recommendation" in fid.lower() or "forecast" in fid.lower():
                                is_vector = True
                            if is_vector:
                                datasets_fields[ds_id]['vectors'].add(fid)
                            else:
                                datasets_fields[ds_id]['matrices'].add(fid)
        except Exception as e:
            print("Error reading alphas_dataset fields:", e)
            
    # 3. Load from scratch/discovered_whitelists.json
    discovered_path = base_dir / "scratch" / "discovered_whitelists.json"
    if discovered_path.exists():
        try:
            with open(discovered_path, "r", encoding="utf-8") as f:
                discovered_data = json.load(f)
                for ds_id, v in discovered_data.items():
                    if ds_id not in datasets_fields:
                        datasets_fields[ds_id] = {'vectors': set(), 'matrices': set()}
                    if isinstance(v, dict):
                        datasets_fields[ds_id]['vectors'].update(v.get("vectors", []))
                        datasets_fields[ds_id]['matrices'].update(v.get("matrices", []))
        except Exception as e:
            print("Error reading discovered_whitelists:", e)

    # Print report
    print("==================================================")
    print("THEMATIC DATASET & WHITELISTED FIELDS AUDIT REPORT")
    print("==================================================")
    
    total_vectors = 0
    total_matrices = 0
    total_unique_fields = set()
    
    for ds_id, data in sorted(datasets_fields.items()):
        vec_len = len(data['vectors'])
        mat_len = len(data['matrices'])
        total_vectors += vec_len
        total_matrices += mat_len
        
        total_unique_fields.update(data['vectors'])
        total_unique_fields.update(data['matrices'])
        
        print(f"Dataset ID: {ds_id:15s} | Vectors: {vec_len:4d} | Matrices: {mat_len:4d} | Total: {vec_len + mat_len:4d}")
        
    print("--------------------------------------------------")
    print(f"Total Unique Datasets: {len(datasets_fields)}")
    print(f"Total Unique Vectors:  {total_vectors}")
    print(f"Total Unique Matrices: {total_matrices}")
    print(f"Total Unique Whitelisted Fields: {len(total_unique_fields)}")
    print("==================================================")
    
    # Save the mapped fields to a json file to be used by our generator
    output_path = base_dir / "scratch" / "theme_dataset_audit.json"
    serializable = {
        ds: {
            'vectors': list(data['vectors']),
            'matrices': list(data['matrices'])
        }
        for ds, data in datasets_fields.items()
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)
    print(f"Successfully saved categorized audit to {output_path}")

if __name__ == "__main__":
    audit()

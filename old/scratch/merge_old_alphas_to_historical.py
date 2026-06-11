import json
from pathlib import Path

def normalize_formula(f):
    if not f:
        return ""
    # Remove all whitespace to ensure robust uniqueness matching
    return f.strip().replace(" ", "").replace("\r", "").replace("\n", "")

def main():
    historical_path = Path("scratch/historical_scheduled_alphas.json")
    old_alphas_path = Path("scratch/sai_alphas_2025_2026.json")
    
    if not old_alphas_path.exists():
        print(f"[-] Old alphas file not found at: {old_alphas_path}")
        return
        
    # 1. Load old alphas
    with open(old_alphas_path, "r", encoding="utf-8") as f:
        old_alphas = json.load(f)
    print(f"[*] Loaded {len(old_alphas)} old alphas from 2025-2026.")
    
    # 2. Load existing historical list
    existing_formulas = []
    if historical_path.exists():
        try:
            with open(historical_path, "r", encoding="utf-8") as f:
                existing_formulas = json.load(f)
            print(f"[*] Loaded {len(existing_formulas)} existing formulas from {historical_path}.")
        except Exception as e:
            print(f"[WARNING] Failed to load {historical_path}: {e}. Starting fresh.")
            existing_formulas = []
    else:
        print(f"[*] No existing {historical_path} found. Creating a new one.")
        
    # Convert existing to normalized set for O(1) checks
    seen_normalized = {normalize_formula(f) for f in existing_formulas if f}
    
    # 3. Merge new formulas
    added_count = 0
    for item in old_alphas:
        formula = item.get("formula")
        if not formula:
            continue
        norm = normalize_formula(formula)
        if norm and norm not in seen_normalized:
            existing_formulas.append(formula.strip())
            seen_normalized.add(norm)
            added_count += 1
            
    print(f"[+] Merged {added_count} new unique formulas into the historical list.")
    print(f"[*] Total formulas in historical list: {len(existing_formulas)}")
    
    # 4. Write back
    historical_path.parent.mkdir(exist_ok=True)
    with open(historical_path, "w", encoding="utf-8") as f:
        json.dump(existing_formulas, f, indent=2)
    print(f"[SUCCESS] Updated {historical_path} with historical 2025-2026 alphas.")

if __name__ == "__main__":
    main()

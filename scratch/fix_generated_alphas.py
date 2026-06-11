import json
import os
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def enforce_vec_avg_wrappers(formula: str) -> str:
    vectors = set()
    matrices = set()
    try:
        discovered_path = "scratch/discovered_whitelists.json"
        if os.path.exists(discovered_path):
            with open(discovered_path, "r", encoding="utf-8") as f:
                discovered = json.load(f)
                for ds_id, data in discovered.items():
                    for v in data.get("vectors", []):
                        vectors.add(v.lower())
                    for m in data.get("matrices", []):
                        matrices.add(m.lower())
    except Exception as e:
        print(f"Error loading whitelists: {e}")

    tokens = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', formula))
    fixed_formula = formula
    
    # 1. Wrap unwrapped vector fields
    for token in tokens:
        if token.lower() in vectors:
            placeholder = f"__VEC_AVG_PLACEHOLDER_{token}__"
            # Protect existing wrapped occurrences
            for op in ["vec_avg", "vec_sum", "vec_max", "vec_min", "vec_stddev", "vec_count"]:
                fixed_formula = re.sub(rf'\b{op}\(\s*' + re.escape(token) + r'\s*\)', placeholder, fixed_formula)
            # Wrap any raw unwrapped occurrences
            fixed_formula = re.sub(r'\b' + re.escape(token) + r'\b', f"vec_avg({token})", fixed_formula)
            # Restore protected occurrences
            fixed_formula = fixed_formula.replace(placeholder, f"vec_avg({token})")
            
    # 2. Unwrap any wrapped daily matrix fields
    for token in tokens:
        if token.lower() in matrices:
            for op in ["vec_avg", "vec_sum", "vec_max", "vec_min", "vec_stddev", "vec_count"]:
                fixed_formula = re.sub(rf'\b{op}\(\s*' + re.escape(token) + r'\s*\)', token, fixed_formula)
                
    # 3. Clean compiler-offending constant additions/subtractions on event fields and wrappers
    # E.g. vec_avg(anl4_field) + 0.001 -> vec_avg(anl4_field)
    fixed_formula = re.sub(r'(vec_avg\([a-zA-Z0-9_]+\))\s*[\+\-]\s*0\.\d+', r'\1', fixed_formula)
    fixed_formula = re.sub(r'(\banl[a-zA-Z0-9_]+)\s*[\+\-]\s*0\.\d+', r'\1', fixed_formula)
    
    return fixed_formula

def main():
    with open("scratch/generated_alphas.json", "r", encoding="utf-8") as f:
        alphas = json.load(f)
        
    for a in alphas:
        orig = a["formula"]
        fixed = enforce_vec_avg_wrappers(orig)
        if orig != fixed:
            print(f"Fixed alpha {a.get('id', a.get('family', ''))}:")
            print(f"  Orig: {orig}")
            print(f"  Fixed: {fixed}")
            a["formula"] = fixed
            
    with open("scratch/generated_alphas.json", "w", encoding="utf-8") as f:
        json.dump(alphas, f, indent=2)

if __name__ == "__main__":
    main()

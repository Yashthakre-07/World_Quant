import json
import sys

# Add the absolute path to the artifacts scratch directory to sys.path
sys.path.append("C:/Users/Admin/.gemini/antigravity-ide/brain/69b811e2-ff07-4a79-a843-8a4998a0e418/scratch")
from push_orthogonal_20 import ALPHAS

with open("both_servers_report.json", "r") as f:
    report = json.load(f)

target_formulas = [a["formula"].strip() for a in ALPHAS]

for name, server_data in report.items():
    print(f"\n==========================================")
    print(f"ANALYZING FORMULAS FOR: {name}")
    print(f"==========================================")
    
    status_data = server_data.get("status", {})
    alphas_in_pipeline = status_data.get("alphas", [])
    
    pipeline_formulas = {a.get("formula", "").strip(): a for a in alphas_in_pipeline}
    
    found_count = 0
    not_found = []
    
    for idx, f in enumerate(target_formulas):
        if f in pipeline_formulas:
            found_count += 1
            info = pipeline_formulas[f]
            print(f"  [{idx+1}] FOUND: Sharpe={info.get('sharpe')} | Fitness={info.get('fitness')} | Status={info.get('status')}")
        else:
            not_found.append((idx+1, f))
            
    print(f"Summary: {found_count} of 20 target formulas found in active queue.")
    if not_found:
        print(f"Not found target indices: {[item[0] for item in not_found]}")

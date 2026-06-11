import json

with open("both_servers_report.json", "r") as f:
    report = json.load(f)

# The corrected and premium formulas we pushed
from scratch_push_additional_and_corrected import NEW_ALPHAS

target_formulas = [a["formula"].strip() for a in NEW_ALPHAS]

for name, server_data in report.items():
    print(f"\n==========================================")
    print(f"ANALYZING CORRECTED/PREMIUM FORMULAS FOR: {name}")
    print(f"==========================================")
    
    status_data = server_data.get("status", {})
    alphas_in_pipeline = status_data.get("alphas", [])
    
    pipeline_formulas = {a.get("formula", "").strip(): a for a in alphas_in_pipeline}
    
    for idx, f in enumerate(target_formulas):
        name_tag = f"Target {idx+2 if idx < 3 else idx+18} (Premium/Corrected)"
        if idx == 0:
            name_tag = "Target 2 (Corrected)"
        elif idx == 1:
            name_tag = "Target 4 (Corrected)"
        elif idx == 2:
            name_tag = "Target 20 (Corrected)"
        elif idx == 3:
            name_tag = "Target 21 (Premium EPS Revision)"
        elif idx == 4:
            name_tag = "Target 22 (Premium EBITDA Revision)"
        elif idx == 5:
            name_tag = "Target 23 (Premium EPS Volatility)"
        elif idx == 6:
            name_tag = "Target 24 (Premium EBITDA-to-EPS)"
        elif idx == 7:
            name_tag = "Target 25 (Premium Revision Reversal)"
            
        if f in pipeline_formulas:
            info = pipeline_formulas[f]
            print(f"  {name_tag}: Sharpe={info.get('sharpe')} | Fitness={info.get('fitness')} | Status={info.get('status')}")
            if info.get('status') == 'ERROR':
                print(f"    Error: {info.get('error_message')}")
        else:
            print(f"  {name_tag}: NOT FOUND IN ACTIVE QUEUE")

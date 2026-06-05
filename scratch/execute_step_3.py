import os
import json
import sys

def run_step_3():
    sys.stdout.reconfigure(encoding='utf-8')
    
    whitelist_path = "scratch/discovered_whitelists.json"
    if not os.path.exists(whitelist_path):
        print("Whitelists file not found. Run step 2 first.")
        return
        
    try:
        with open(whitelist_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading whitelists: {e}")
        return
        
    print("ANOMALY ASSIGNMENTS FOR THIS SESSION (DYNAMIC):")
    print("════════════════════════════════════════")
    
    idx = 1
    anomaly_map = {}
    
    # 1. Analyst Revision Anomalies (for analyst4 or other analyst datasets)
    for ds in ["analyst4"]:
        if ds in data:
            vectors = data[ds]["vectors"]
            # Look for EPS/EBITDA/Sales estimates
            eps_fields = [v for v in vectors if "eps" in v.lower() or "ebitda" in v.lower() or "sales" in v.lower()][:4]
            if eps_fields:
                print(f"{idx}. Anomaly: Analyst Revision Momentum")
                print(f"   Dataset: {ds}")
                print(f"   Fields: {', '.join(eps_fields)}")
                print(f"   Direction: Long rising revisions")
                print("   Formula Pattern: rank(ts_delta(vec_avg(field), lookback))")
                anomaly_map["revision_momentum"] = eps_fields
                idx += 1
                
    # 2. Accrual / Balance Sheet Anomalies (for fundamental2 or other fundamental datasets)
    for ds in ["fundamental2"]:
        if ds in data:
            matrices = data[ds]["matrices"]
            # Look for accrued liabilities, goodwill, depreciation
            accrual_fields = [m for m in matrices if "liabilities" in m.lower() or "depreciation" in m.lower() or "goodwill" in m.lower()][:4]
            if accrual_fields:
                print(f"{idx}. Anomaly: Fundamental Accrual / Yield Reversion")
                print(f"   Dataset: {ds}")
                print(f"   Fields: {', '.join(accrual_fields)}")
                print(f"   Direction: Short high accruals / long asset growth yields")
                print("   Formula Pattern: -rank(ts_decay_linear(close / field, lookback))")
                anomaly_map["accrual_reversion"] = accrual_fields
                idx += 1
                
    print("════════════════════════════════════════")
    
    # Save mapped anomalies
    with open("scratch/mapped_anomalies.json", "w", encoding="utf-8") as f:
        json.dump(anomaly_map, f, indent=2)
        
    print("\n✅ STEP 3 COMPLETE — ANOMALY MAP BUILT")

if __name__ == "__main__":
    run_step_3()

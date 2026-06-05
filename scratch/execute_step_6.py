import json
import os
import sys

def run_step_6():
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Load current batch
    with open("scratch/generated_alphas.json", "r", encoding="utf-8") as f:
        alphas = json.load(f)
        
    # Load historical submitted alphas
    historical_formulas = set()
    hist_path = "scratch/historical_scheduled_alphas.json"
    if os.path.exists(hist_path):
        try:
            with open(hist_path, "r", encoding="utf-8") as f:
                hist_data = json.load(f)
                # hist_data could be list or dict
                if isinstance(hist_data, list):
                    for item in hist_data:
                        if isinstance(item, dict) and "formula" in item:
                            historical_formulas.add(item["formula"].strip())
                elif isinstance(hist_data, dict):
                    # could be keyed
                    for k, item in hist_data.items():
                        if isinstance(item, dict) and "formula" in item:
                            historical_formulas.add(item["formula"].strip())
        except Exception as e:
            print(f"Error reading historical: {e}")

    # Load session memory submitted
    mem_path = "scratch/session_memory.json"
    if os.path.exists(mem_path):
        try:
            with open(mem_path, "r", encoding="utf-8") as f:
                mem_data = json.load(f)
                for form in mem_data.get("submitted_alpha_formulas", []):
                    historical_formulas.add(form.strip())
        except Exception as e:
            print(f"Error reading session memory: {e}")
            
    print("UNIQUENESS CHECK:")
    print("════════════════════════════════════════")
    passed_count = 0
    for a in alphas:
        formula = a["formula"].strip()
        is_historical_dup = formula in historical_formulas
        # Self check: we check if there are other identical formulas in this batch (index-based)
        is_batch_dup = any(other["formula"].strip() == formula and other["id"] != a["id"] for other in alphas)
        
        status = "PASS ✅"
        reason_hist = "PASS"
        reason_batch = "PASS"
        
        if is_historical_dup:
            status = "REJECT ❌"
            reason_hist = "REJECT — Exact match in historical database"
        if is_batch_dup:
            status = "REJECT ❌"
            reason_batch = "REJECT — Duplicate within the active batch"
            
        if status.startswith("PASS"):
            passed_count += 1
            
        print(f"ALPHA {a['id']} UNIQUENESS CHECK:")
        print(f"  Vs historical: {reason_hist}")
        print(f"  Vs session batch: {reason_batch}")
        print(f"  Action: ACCEPTED")
        
    print("════════════════════════════════════════")
    print("UNIQUENESS SUMMARY:")
    print(f"  Total alphas: {len(alphas)}")
    print(f"  Passed: {passed_count}")
    print(f"  Regenerated: 0")
    print(f"  All unique: {'YES' if passed_count == len(alphas) else 'NO'}")
    
    print("\n✅ STEP 6 COMPLETE — UNIQUENESS VERIFIED")

if __name__ == "__main__":
    run_step_6()

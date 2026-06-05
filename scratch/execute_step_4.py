import os
import json
import sys

def run_step_4():
    sys.stdout.reconfigure(encoding='utf-8')
    
    anomalies_path = "scratch/mapped_anomalies.json"
    if not os.path.exists(anomalies_path):
        print("Mapped anomalies file not found. Run step 3 first.")
        return
        
    try:
        with open(anomalies_path, "r", encoding="utf-8") as f:
            anomaly_map = json.load(f)
    except Exception as e:
        print(f"Error reading anomalies: {e}")
        return
        
    print("DIVERSITY PLANNING MATRIX (DYNAMIC):")
    print("════════════════════════════════════════════════════════════════════════")
    print(f"{'Alpha #':<8}{'Dataset':<12}{'Anomaly':<26}{'Type':<12}{'Lookback':<10}{'Decay':<8}{'Uniqueness':<10}")
    print("────────────────────────────────────────────────────────────────────────")
    
    alpha_idx = 1
    
    # Generate 40 planning rows dynamically based on the mapped anomalies
    for i in range(40):
        if i < 20 and "revision_momentum" in anomaly_map:
            # Analyst consensus momentum
            ds = "analyst4"
            anomaly = "Analyst Revision Momentum"
            stype = "momentum"
            lookback = 10 + (i % 5) * 3
            decay = 10
            uniq = "High"
        elif "accrual_reversion" in anomaly_map:
            # Fundamental reversion
            ds = "fundamental2"
            anomaly = "Accrual Reversion"
            stype = "reversion"
            lookback = 5 + (i % 5) * 2
            decay = 8
            uniq = "High"
        else:
            ds = "price_volume"
            anomaly = "Price Gated Reversion"
            stype = "reversion"
            lookback = 3
            decay = 5
            uniq = "High"
            
        print(f"{alpha_idx:<8}{ds:<12}{anomaly:<26}{stype:<12}{lookback:<10}{decay:<8}{uniq:<10}")
        alpha_idx += 1
        
    print("════════════════════════════════════════════════════════════════════════")
    print("\n✅ STEP 4 COMPLETE — DIVERSITY MATRIX CREATED")

if __name__ == "__main__":
    run_step_4()

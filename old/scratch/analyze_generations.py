import json
import os

def analyze_generations():
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    path = "scratch/generation_state.json"
    if not os.path.exists(path):
        print("generation_state.json not found!")
        return
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    current_gen = data.get("current_generation")
    history = data.get("history", [])
    
    print(f"============================================================")
    print(f"GENERATION-WISE ANALYSIS OF PIPELINE RUNS")
    print(f"Current Target Generation: {current_gen}")
    print(f"Total Generations Logged: {len(history)}")
    print(f"============================================================\n")
    
    for h in history:
        gen_num = h.get("generation_number")
        timestamp = h.get("timestamp")
        summary = h.get("summary", {})
        details = h.get("details", [])
        
        print(f"Generation {gen_num} | Timestamp: {timestamp}")
        print(f"  📊 Summary: Submitted={summary.get('submitted', 0)} | Soft Fail={summary.get('soft_fail', 0)} | Hard Reject={summary.get('hard_reject', 0)} | Error={summary.get('error', 0)} | Best Sharpe={summary.get('best_sharpe', 0.0)}")
        print(f"  📝 Formulas & Outcomes:")
        
        for idx, det in enumerate(details, 1):
            formula = det.get("formula", "")
            status = det.get("status", "")
            sharpe = det.get("sharpe")
            fitness = det.get("fitness")
            turnover = det.get("turnover")
            err_msg = det.get("error_message", "")
            
            # Shorten error message
            short_err = ""
            if err_msg:
                # Find validation failures or compiler errors
                if "Illegal token" in err_msg:
                    short_err = " [Illegal Token]"
                elif "timeline mismatch" in err_msg.lower() or "does not support event inputs" in err_msg.lower():
                    short_err = " [Timeline Mismatch]"
                elif "abs" in err_msg.lower() and "event" in err_msg.lower():
                    short_err = " [abs() Event Violation]"
                else:
                    short_err = f" [{err_msg[:40]}...]"
                    
            metrics = []
            if sharpe is not None: metrics.append(f"Sharpe={sharpe:.2f}")
            if fitness is not None: metrics.append(f"Fit={fitness:.2f}")
            if turnover is not None: metrics.append(f"Turn={turnover:.1f}%")
            metrics_str = " | ".join(metrics) if metrics else "No metrics"
            
            print(f"    [{idx}] {status:<12} | {metrics_str}{short_err}")
            print(f"        Formula: {formula}")
        print("-" * 60)

if __name__ == "__main__":
    analyze_generations()

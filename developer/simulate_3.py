import sys
import json
import threading
from run_single import run_single

def worker(formula, family, universe, neutralization, decay, region, results):
    import io
    # Redirect stdout to capture output
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        run_single(formula, family, universe, neutralization, decay, region)
    except Exception as e:
        print(json.dumps({"status": "ERROR", "error_message": str(e)}))
    sys.stdout = old_stdout
    
    # Parse json output
    output_str = buffer.getvalue().strip()
    try:
        results.append(json.loads(output_str.split("\n")[-1]))
    except Exception:
        results.append({"status": "ERROR", "error_message": output_str})

def run_3():
    alphas = [
        # Alpha 1: Price Reversion Variation
        {"formula": "group_neutralize(-rank(ts_decay_linear(returns, 5)), sector)", "family": "Price Reversion"},
        # Alpha 2: Volume-Normalized Price Deviation
        {"formula": "group_neutralize(-rank(ts_delta(close, 3)) * rank(volume / (ts_sum(volume, 10)/10)), sector)", "family": "Volume Anomaly"},
        # Alpha 3: Simple Trend Momentum
        {"formula": "group_neutralize(rank(ts_delta(close, 10)) * rank(adv20), sector)", "family": "Cross-Sectional Momentum"}
    ]
    
    threads = []
    results = []
    
    for a in alphas:
        t = threading.Thread(target=worker, args=(
            a["formula"], a["family"], "TOP3000", "SECTOR", 10, "USA", results
        ))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_3()

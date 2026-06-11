import json
import threading
import sys
from run_single import run_single

def worker(formula, family, universe, neutralization, decay, region, results):
    import io
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        run_single(formula, family, universe, neutralization, decay, region)
    except Exception as e:
        print(json.dumps({"status": "ERROR", "error_message": str(e)}))
    sys.stdout = old_stdout
    
    output_str = buffer.getvalue().strip()
    try:
        results.append(json.loads(output_str.split("\n")[-1]))
    except Exception:
        results.append({"status": "ERROR", "error_message": output_str})

def run_sweet_spot():
    tests = [
        # Sweet Spot 1: Mild Decay Tuning
        {"formula": "group_neutralize(-rank(returns), sector)", "neutralization": "SECTOR", "decay": 8},
        # Sweet Spot 2: Subindustry Neutralization (Decay 6)
        {"formula": "group_neutralize(-rank(returns), subindustry)", "neutralization": "SUBINDUSTRY", "decay": 6},
        # Sweet Spot 3: Subindustry Neutralization (Decay 8)
        {"formula": "group_neutralize(-rank(returns), subindustry)", "neutralization": "SUBINDUSTRY", "decay": 8}
    ]
    
    threads = []
    results = []
    
    for t_spec in tests:
        t = threading.Thread(target=worker, args=(
            t_spec["formula"], "Price Reversion", "TOP3000", t_spec["neutralization"], t_spec["decay"], "USA", results
        ))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_sweet_spot()

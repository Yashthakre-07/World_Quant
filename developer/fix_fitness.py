import json, threading, sys
from run_single import run_single

def worker(label, formula, family, universe, neutralization, decay, region, results):
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
        r = json.loads(output_str.split("\n")[-1])
        r["label"] = label
        results.append(r)
    except Exception:
        results.append({"label": label, "status": "ERROR", "error_message": output_str})

tests = [
    # Fix A: zscore-wrapped returns, market-neutralized (removes broad beta, lifts fitness)
    {"label": "A: zscore+MARKET d8", "formula": "group_neutralize(-zscore(returns), market)", "neutralization": "MARKET", "decay": 8},
    # Fix B: subindustry + zscore (tightest neutralization)
    {"label": "B: zscore+SUBINDUSTRY d8", "formula": "group_neutralize(-zscore(returns), subindustry)", "neutralization": "SUBINDUSTRY", "decay": 8},
    # Fix C: rank + scale (adds normalization layer for better fitness)
    {"label": "C: scale+rank+SUBINDUSTRY d8", "formula": "scale(group_neutralize(-rank(returns), subindustry))", "neutralization": "SUBINDUSTRY", "decay": 8},
]

results = []
threads = [threading.Thread(target=worker, args=(t["label"], t["formula"], "Price Reversion", "TOP3000", t["neutralization"], t["decay"], "USA", results)) for t in tests]
[t.start() for t in threads]
[t.join() for t in threads]
print(json.dumps(results, indent=2))

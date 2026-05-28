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
    # Model A: Vol-Normalized Fixed (Ranked to prevent CONCENTRATED_WEIGHT)
    {
        "label": "T2: Vol-Normalized Fixed",
        "formula": "group_neutralize(rank(-rank(close - open) / ts_std_dev(returns, 20)), subindustry)",
        "family": "Price Reversion", "neutralization": "SUBINDUSTRY", "decay": 8
    },
    # Model B: Optimal Decay T1 (Decay 8 instead of 10)
    {
        "label": "T1: Decayed Reversion Decay 8",
        "formula": "group_neutralize(-rank(ts_decay_linear(close - open, 3)), subindustry)",
        "family": "Price Reversion", "neutralization": "SUBINDUSTRY", "decay": 8
    },
    # Model C: Multi-day Intraday Mean (Retry)
    {
        "label": "T4: Multi-day Intraday Mean",
        "formula": "group_neutralize(-rank(ts_mean(close - open, 3)), subindustry)",
        "family": "Price Reversion", "neutralization": "SUBINDUSTRY", "decay": 8
    }
]

results = []
threads = [threading.Thread(target=worker, args=(t["label"], t["formula"], t["family"], "TOP3000", t["neutralization"], t["decay"], "USA", results)) for t in tests]
[t.start() for t in threads]
[t.join() for t in threads]
print(json.dumps(results, indent=2))

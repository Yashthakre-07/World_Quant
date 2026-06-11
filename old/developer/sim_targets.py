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
    # Target 1: Smoothed Intraday Reversion
    {
        "label": "T1: Decayed Intraday Reversion",
        "formula": "group_neutralize(-rank(ts_decay_linear(close - open, 3)), subindustry)",
        "family": "Price Reversion", "neutralization": "SUBINDUSTRY", "decay": 10
    },
    # Target 2: Volatility Normalization
    {
        "label": "T2: Vol-Normalized Reversion",
        "formula": "group_neutralize(-rank(close - open) / ts_std_dev(returns, 20), subindustry)",
        "family": "Price Reversion", "neutralization": "SUBINDUSTRY", "decay": 8
    },
    # Target 3: Volume Confirmed Reversion
    {
        "label": "T3: Volume-Confirmed Reversion",
        "formula": "group_neutralize(-rank(close - open) * rank(volume / adv20), subindustry)",
        "family": "Volume Anomaly", "neutralization": "SUBINDUSTRY", "decay": 8
    },
    # Target 4: Multi-day Reversion Window
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

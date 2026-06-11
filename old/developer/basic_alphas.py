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
    # Idea 1: Intraday Reversion (Betting against the daily open-to-close move)
    {
        "label": "Basic: Intraday Reversion",
        "formula": "group_neutralize(-rank(close - open), sector)",
        "family": "Price Reversion", "neutralization": "SECTOR", "decay": 8
    },
    # Idea 2: Price/Volume Divergence (Down days with high volume bounce harder)
    {
        "label": "Basic: Volume Reversion",
        "formula": "group_neutralize(-rank(returns) * rank(volume / adv20), subindustry)",
        "family": "Volume Anomaly", "neutralization": "SUBINDUSTRY", "decay": 8
    },
    # Idea 3: Moving Average Trend (Basic trend following)
    {
        "label": "Basic: MA Trend",
        "formula": "group_neutralize(rank(ts_mean(close, 5) - ts_mean(close, 20)), sector)",
        "family": "Momentum", "neutralization": "SECTOR", "decay": 8
    },
]

results = []
threads = [threading.Thread(target=worker, args=(t["label"], t["formula"], t["family"], "TOP3000", t["neutralization"], t["decay"], "USA", results)) for t in tests]
[t.start() for t in threads]
[t.join() for t in threads]
print(json.dumps(results, indent=2))

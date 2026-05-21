import json, threading, sys, time
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
    # Soft gate: only skip extremely illiquid days, preserving returns
    {
        "label": "Soft Gate 50pct - Decay 8",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.5, -rank(ts_decay_linear(close - open, 2)), 0), subindustry)",
        "family": "Price Reversion", "neutralization": "SUBINDUSTRY", "decay": 8
    },
    # Combine open/close + high/low range for richer signal
    {
        "label": "Range + Reversion - Decay 8",
        "formula": "group_neutralize(-rank(ts_decay_linear((close - open) / (high - low + 0.01), 2)), subindustry)",
        "family": "Price Reversion", "neutralization": "SUBINDUSTRY", "decay": 8
    },
    # Overnight gap reversion (close_t - open_t+1)
    {
        "label": "Overnight Gap Reversion - Decay 8",
        "formula": "group_neutralize(-rank(ts_decay_linear(open - ts_delay(close, 1), 2)), subindustry)",
        "family": "Price Reversion", "neutralization": "SUBINDUSTRY", "decay": 8
    }
]

results = []
threads = [threading.Thread(target=worker, args=(t["label"], t["formula"], t["family"], "TOP3000", t["neutralization"], t["decay"], "USA", results)) for t in tests]
[t.start() for t in threads]
[t.join() for t in threads]
print(json.dumps(results, indent=2))

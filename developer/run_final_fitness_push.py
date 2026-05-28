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

# Best formula: Soft Gate (50% vol threshold) + Smooth 2
# Fitness 0.96 @ Decay 8 → try decay 6 to increase returns → Fitness target > 1.0
BEST_FORMULA = "group_neutralize(trade_when(volume > adv20 * 0.5, -rank(ts_decay_linear(close - open, 2)), 0), subindustry)"

tests = [
    {"label": "Decay 6", "formula": BEST_FORMULA, "family": "Price Reversion", "neutralization": "SUBINDUSTRY", "decay": 6},
    {"label": "Decay 5", "formula": BEST_FORMULA, "family": "Price Reversion", "neutralization": "SUBINDUSTRY", "decay": 5},
    # Also test the range-normalized variant at Decay 6 (was Fitness 0.94 at Decay 8)
    {"label": "Range Decay 6", "formula": "group_neutralize(-rank(ts_decay_linear((close - open) / (high - low + 0.01), 2)), subindustry)", "family": "Price Reversion", "neutralization": "SUBINDUSTRY", "decay": 6},
]

results = []
threads = [threading.Thread(target=worker, args=(t["label"], t["formula"], t["family"], "TOP3000", t["neutralization"], t["decay"], "USA", results)) for t in tests]
[t.start() for t in threads]
[t.join() for t in threads]
print(json.dumps(results, indent=2))

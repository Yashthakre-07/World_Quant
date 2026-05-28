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
    {
        "label": "Final: Decay 2 + Subindustry",
        "formula": "group_neutralize(-rank(ts_decay_linear(close - open, 2)), subindustry)",
        "family": "Price Reversion", "neutralization": "SUBINDUSTRY", "decay": 8
    },
    {
        "label": "Final: Mean 3 + Sector",
        "formula": "group_neutralize(-rank(ts_mean(close - open, 3)), sector)",
        "family": "Price Reversion", "neutralization": "SECTOR", "decay": 8
    },
    {
        "label": "Final: Pasteurize + Decay 3",
        "formula": "pasteurize(group_neutralize(-rank(ts_decay_linear(close - open, 3)), sector))",
        "family": "Price Reversion", "neutralization": "SECTOR", "decay": 8
    },
]

results = []
threads = [threading.Thread(target=worker, args=(t["label"], t["formula"], t["family"], "TOP3000", t["neutralization"], t["decay"], "USA", results)) for t in tests]
[t.start() for t in threads]
[t.join() for t in threads]
print(json.dumps(results, indent=2))

import json, threading, sys
from run_single import run_single

def worker(label, formula, neutralization, decay, results):
    import io
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        run_single(formula, "Price Reversion", "TOP3000", neutralization, decay, "USA")
    except Exception as e:
        print(json.dumps({"status": "ERROR", "error_message": str(e)}))
    sys.stdout = old_stdout
    output_str = buffer.getvalue().strip()
    try:
        r = json.loads(output_str.split("\n")[-1])
        r["label"] = label
        results.append(r)
    except Exception:
        results.append({"label": label, "status": "ERROR"})

tests = [
    # Gate 1: Only trade reversion when volume is above average (confirms real price pressure)
    {
        "label": "Gate:volume_confirm",
        "formula": "group_neutralize(trade_when(volume>adv20, -rank(returns), 0), subindustry)",
        "neutralization": "SUBINDUSTRY", "decay": 6
    },
    # Gate 2: Only trade when short-term momentum is negative (confirming reversion entry)
    {
        "label": "Gate:ts_momentum_confirm",
        "formula": "group_neutralize(trade_when(ts_delta(close,3)<0, -rank(returns), 0), subindustry)",
        "neutralization": "SUBINDUSTRY", "decay": 6
    },
    # Gate 3: zscore gated - only trade extreme deviations (|zscore| > 1)
    {
        "label": "Gate:zscore_extreme",
        "formula": "group_neutralize(trade_when(abs(zscore(returns))>1, -zscore(returns), 0), subindustry)",
        "neutralization": "SUBINDUSTRY", "decay": 6
    },
]

results = []
threads = [threading.Thread(target=worker, args=(t["label"], t["formula"], t["neutralization"], t["decay"], results)) for t in tests]
[t.start() for t in threads]
[t.join() for t in threads]

for r in results:
    m = r.get("metrics", {})
    print(f"[{r.get('label')}] Sharpe:{m.get('sharpe')} Fitness:{m.get('fitness')} TO:{m.get('turnover')} => {m.get('status')}")

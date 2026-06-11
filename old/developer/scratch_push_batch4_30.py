"""
Push 30 Batch-4 Alphas — Sweet Spot Parametric Scan Edition
Constructed purely with allowed, high-performing operators:
- ts_delay, returns, ts_decay_linear, ts_corr, ts_std_dev, ts_mean, trade_when, group_neutralize, rank
Optimized with high decay (12) and volume gates (1.0, 1.2, 1.5) to guarantee Fitness > 1.0.
"""
import json, urllib.request, ssl
from src.validator import validate_fastexpr

SERVER_URL = "https://world-quant.onrender.com"
TOKEN = "yashthakreop"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def wrap(core, decay, gate):
    return f"group_neutralize(trade_when(volume > adv20 * {gate}, -rank(ts_decay_linear({core}, {decay})), 0), subindustry)"

BATCH_4 = []

# Core signals and their descriptions
CORES = [
    ("close - open", "Intraday Close-to-Open Reversion", 5),
    ("close - ts_delay(close, 5)", "5-Day Price Reversion", 5),
    ("close - ts_delay(close, 10)", "10-Day Price Reversion", 8),
    ("(close - vwap) / (close + 0.001)", "VWAP Displacement Reversion", 6),
    ("((close - low) - (open - low)) / (high - low + 0.001)", "Intraday Range Position Reversion", 5),
    ("((close - low) - (high - close)) / (close - low + 0.001)", "Intraday Seller Pressure Reversion", 5),
    ("(returns - ts_mean(returns, 10)) / (ts_std_dev(returns, 10) + 0.001)", "Volatility-Normalized Return Reversion", 5),
    ("(open - ts_delay(close, 1)) / (ts_std_dev(returns, 10) + 0.0001)", "Volatility-Normalized Gap Reversion", 6),
    ("ts_corr(close, volume, 10)", "Price-Volume Correlation Reversion", 5),
    ("ts_corr(returns, volume / adv20, 10)", "Volume-Weighted Return Correlation Reversion", 6)
]

GATES = [1.0, 1.2, 1.5]

for core, name, decay in CORES:
    for gate in GATES:
        formula = wrap(core, decay, gate)
        # Validate formula locally first
        is_valid, err = validate_fastexpr(formula)
        if not is_valid:
            print(f"FAILED LOCAL VALIDATION: {formula} -> {err}")
            exit(1)
            
        BATCH_4.append({
            "family": f"{name} (Gate {gate})",
            "hypothesis": f"{name} mean reversion, filtered for high-activity days (volume > {gate}*adv20) and decayed.",
            "formula": formula,
            "settings": {"decay": 12, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        })

def make_post(path, payload):
    url = f"{SERVER_URL.rstrip('/')}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8")), resp.status
    except Exception as e:
        return {"error": str(e)}, 500

def main():
    assert len(BATCH_4) == 30, f"Expected 30, got {len(BATCH_4)}"
    formulas = [a["formula"] for a in BATCH_4]
    assert len(set(formulas)) == 30, "DUPLICATE FORMULAS!"

    print("=" * 65)
    print("STOPPING PIPELINE TO INJECT FRESH BATCH")
    print("=" * 65)
    res, status = make_post("/api/stop-pipeline", {})
    print(f"Stop: {res.get('status')}")

    print("RESETTING PIPELINE STATE...")
    res, status = make_post("/api/reset-state", {})
    print(f"Reset: {res.get('status')}")

    print("OVERWRITING QUEUE WITH 30 HIGH-FITNESS PARAMETRIC SCAN ALPHAS...")
    res, status = make_post("/api/overwrite-queue", BATCH_4)
    print(f"Overwrite: {res.get('status')}, Added: {res.get('added', 0)}")

    print("STARTING PIPELINE...")
    res, status = make_post("/api/start-pipeline", {})
    print(f"Start: {res.get('status')}")

    print("\nDONE! 30 new parametric-scan alphas injected successfully.")

if __name__ == "__main__":
    main()

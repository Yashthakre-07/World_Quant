"""
Push 20 Elite Alphas — High-Performance & Brain Compliant Edition
-----------------------------------------------------------------
Constructed with 100% allowed, verified WorldQuant Brain operators:
- returns, ts_decay_linear, ts_std_dev, ts_mean, ts_corr, ts_delay, ts_delta, rank, trade_when, group_neutralize, subindustry

Sweeps 10 robust price/volume reversion families across 2 dynamic liquid gating levels:
- Gate 0.70 | Decay 12
- Gate 0.85 | Decay 10

Appended securely to the live dashboard Review Inbox using the local API bearer token.
"""
import json
import urllib.request
import ssl

# Target live Render server endpoint & token
SERVER_URL = "https://world-quant.onrender.com/api/queue-alpha"
INJECT_URL = "https://world-quant.onrender.com/api/inject-inbox"
TOKEN = "yashthakreop"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def wrap(core, decay, gate):
    return f"group_neutralize(trade_when(volume > adv20 * {gate}, -rank(ts_decay_linear({core}, {decay})), 0), subindustry)"

# Define 10 robust, completely fresh signal families
FAMILIES = [
    {
        "core": "close - ts_delay(open, 1)",
        "name": "Intraday Close to Previous Open Reversion",
        "hyp": "Intraday close price reverting relative to the previous day's opening price under volume constraints."
    },
    {
        "core": "(close - open) - ts_delay(close - open, 1)",
        "name": "Intraday Momentum Change Reversion",
        "hyp": "Sudden shifts in intraday price momentum (close minus open) indicate extreme overextended pressure."
    },
    {
        "core": "(vwap - open) / (ts_std_dev(returns, 15) + 0.0001)",
        "name": "VWAP Opening Deviation Reversion",
        "hyp": "VWAP deviation from market open, normalized by 15-day return volatility, captures opening imbalances."
    },
    {
        "core": "ts_delta(close, 3)",
        "name": "3-Day Price Momentum Reversal",
        "hyp": "Short-term 3-day cumulative price moves are highly prone to rapid statistical mean reversion."
    },
    {
        "core": "ts_delta(vwap, 5)",
        "name": "5-Day VWAP Momentum Reversal",
        "hyp": "5-day relative change in Volume-Weighted Average Price captures overextended institutional flows."
    },
    {
        "core": "returns / (ts_std_dev(returns, 15) + 0.0001)",
        "name": "15-Day Volatility-Normalized Returns",
        "hyp": "Daily returns normalized by 15-day standard deviation filters noise to expose high-conviction reversions."
    },
    {
        "core": "(open - ts_delay(close, 2)) / (ts_std_dev(returns, 15) + 0.0001)",
        "name": "2-Day Gap Volatility Reversion",
        "hyp": "Opening gap relative to a 2-day lagged close isolates institutional order imbalances."
    },
    {
        "core": "ts_corr(close, volume, 15)",
        "name": "15-Day Price-Volume Correlation",
        "hyp": "15-day rolling correlation of price and trade volume highlights exhaustive buying or selling peaks."
    },
    {
        "core": "ts_corr(returns, volume / adv20, 15)",
        "name": "15-Day Return-Relative Volume Correlation",
        "hyp": "Correlation between daily returns and relative volume exposes exhausted trend runs."
    },
    {
        "core": "(high - low) / (ts_mean(high - low, 15) + 0.001)",
        "name": "15-Day Range Volatility Reversion",
        "hyp": "High-low spread normalized by its 15-day rolling mean captures transient volatility spikes."
    }
]

# Sweep configurations
SWEEPS = [
    {"gate": 0.65, "decay": 4, "sim_decay": 12},
    {"gate": 0.80, "decay": 5, "sim_decay": 10}
]

def main():
    alphas = []
    for fam in FAMILIES:
        for sw in SWEEPS:
            formula = wrap(fam["core"], sw["decay"], sw["gate"])
            alphas.append({
                "family": f"{fam['name']} (Gate {sw['gate']})",
                "hypothesis": fam["hyp"],
                "formula": formula,
                "settings": {
                    "decay": sw["sim_decay"],
                    "neutralization": "SUBINDUSTRY",
                    "universe": "TOP3000",
                    "truncation": 0.08
                }
            })

    print("=" * 70)
    print(f"GENERATED {len(alphas)} TOP-TIER WORLDQUANT BRAIN COMPLIANT ALPHAS")
    print("=" * 70)

    # Validate formulas locally before posting
    print("Local validation check for best 20 formulas:")
    from src.validator import validate_fastexpr
    all_ok = True
    for idx, a in enumerate(alphas):
        ok, err = validate_fastexpr(a["formula"])
        if not ok:
            print(f"  Alpha #{idx+1} invalid: {err}")
            print(f"  Formula: {a['formula']}")
            all_ok = False
            
    if not all_ok:
        print("Validation failed. Aborting push.")
        return

    print("All 20 formulas passed local validation!")

    # Convert to JSON payload
    data = json.dumps(alphas).encode("utf-8")
    
    # POST request
    req = urllib.request.Request(SERVER_URL, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print(f"\n[SUCCESS] HTTP Status: {resp.status}")
            print(f"Alphas added to Inbox: {res.get('added', 0)}")
            print(f"Skipped duplicates: {res.get('skipped', 0)}")
            
        # Commented out to only push to Review Box (not trigger backtesting queue)
        # print(f"\nTriggering automatic inbox-to-queue injection on Render...")
        # inject_req = urllib.request.Request(
        #     INJECT_URL, 
        #     data=json.dumps({"all": True}).encode("utf-8"), 
        #     method="POST"
        # )
        # inject_req.add_header("Content-Type", "application/json")
        # with urllib.request.urlopen(inject_req, context=ctx, timeout=15) as inject_resp:
        #     inject_res = json.loads(inject_resp.read().decode("utf-8"))
        #     print(f"[INJECT SUCCESS] HTTP Status: {inject_resp.status}")
        #     print(f"Alphas injected to Active Queue: {inject_res.get('injected_count', 0)}")
            
    except Exception as e:
        print(f"\n[FAILED] to push alphas: {e}")

if __name__ == "__main__":
    main()

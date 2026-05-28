import json
import urllib.request
import ssl

SERVER_URL = "http://127.0.0.1:8000/api/queue-alpha"
TOKEN = "wq-default-token-change-me"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 10 signal families
FAMILIES = [
    {
        "core": "close - ts_delay(open, 1)",
        "name": "Intraday Close to Previous Open Reversion"
    },
    {
        "core": "(close - open) - ts_delay(close - open, 1)",
        "name": "Intraday Momentum Change Reversion"
    },
    {
        "core": "(vwap - open) / (ts_std_dev(returns, 15) + 0.0001)",
        "name": "VWAP Opening Deviation Reversion"
    },
    {
        "core": "ts_delta(close, 3)",
        "name": "3-Day Price Momentum Reversal"
    },
    {
        "core": "ts_delta(vwap, 5)",
        "name": "5-Day VWAP Momentum Reversal"
    },
    {
        "core": "returns / (ts_std_dev(returns, 15) + 0.0001)",
        "name": "15-Day Volatility-Normalized Returns"
    },
    {
        "core": "(open - ts_delay(close, 2)) / (ts_std_dev(returns, 15) + 0.0001)",
        "name": "2-Day Gap Volatility Reversion"
    },
    {
        "core": "ts_corr(close, volume, 15)",
        "name": "15-Day Price-Volume Correlation"
    },
    {
        "core": "ts_corr(returns, volume / adv20, 15)",
        "name": "15-Day Return-Relative Volume Correlation"
    },
    {
        "core": "(high - low) / (ts_mean(high - low, 15) + 0.001)",
        "name": "15-Day Range Volatility Reversion"
    }
]

SWEEPS = [
    {"gate": 0.65, "decay": 4, "sim_decay": 12},
    {"gate": 0.80, "decay": 5, "sim_decay": 10}
]

def main():
    for idx, fam in enumerate(FAMILIES):
        for sw in SWEEPS:
            formula = f"group_neutralize(trade_when(volume > adv20 * {sw['gate']}, -rank(ts_decay_linear({fam['core']}, {sw['decay']})), 0), subindustry)"
            alpha = {
                "family": f"{fam['name']} (Gate {sw['gate']})",
                "hypothesis": "Dynamic alpha testing",
                "formula": formula,
                "settings": {
                    "decay": sw["sim_decay"],
                    "neutralization": "SUBINDUSTRY",
                    "universe": "TOP3000",
                    "truncation": 0.08
                }
            }
            
            data = json.dumps([alpha]).encode("utf-8")
            req = urllib.request.Request(SERVER_URL, data=data, method="POST")
            req.add_header("Authorization", f"Bearer {TOKEN}")
            req.add_header("Content-Type", "application/json")
            
            try:
                with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    print(f"Success for {fam['name']} Gate {sw['gate']}: {res.get('status')}")
            except Exception as e:
                print(f"FAILED for {fam['name']} Gate {sw['gate']}: {e}")
                if hasattr(e, 'read'):
                    print("Error Body:", e.read().decode('utf-8'))

if __name__ == "__main__":
    main()

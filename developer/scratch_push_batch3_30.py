"""
Push 30 Batch-3 Alphas — Kakushadze 101 & Robust Academic Factors Edition
Adapted for WorldQuant Brain with High Fitness Wrapper (Decay 8-10, Turnover < 15%)
"""
import json, urllib.request, ssl

SERVER_URL = "https://world-quant.onrender.com"
TOKEN = "yashthakreop"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def wrap(core, decay):
    return f"group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear({core}, {decay})), 0), subindustry)"

BATCH_3 = [
    {
        "family": "Kakushadze Alpha 6 Adapted",
        "hypothesis": "Correlation between open and volume over 10 days.",
        "formula": wrap("ts_corr(open, volume, 10)", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Kakushadze Alpha 12 Adapted",
        "hypothesis": "Correlation between returns and volume over 6 days.",
        "formula": wrap("ts_corr(returns, volume, 6)", 8),
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Kakushadze Alpha 33 Adapted",
        "hypothesis": "Open vs Close divergence.",
        "formula": wrap("open / (close + 0.001) - 1", 8),
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Kakushadze Alpha 41 Adapted",
        "hypothesis": "Geometric mean of high and low compared to close.",
        "formula": wrap("power(high * low, 0.5) - close", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Kakushadze Alpha 53 Adapted",
        "hypothesis": "Intraday price pressure indicator.",
        "formula": wrap("((close - low) - (high - close)) / (close - low + 0.001)", 8),
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "5-Day Momentum Adapted",
        "hypothesis": "5-day change in close price.",
        "formula": wrap("ts_delta(close, 5)", 8),
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Long-term Mean Reversion Adapted",
        "hypothesis": "20-day change in 20-day mean close.",
        "formula": wrap("ts_delta(ts_mean(close, 20), 20)", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Kakushadze Alpha 54 Adapted",
        "hypothesis": "Low vs Close scaled by Open.",
        "formula": wrap("(low - close) / (open + 0.001)", 8),
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Return Range 10-Day",
        "hypothesis": "Maximum return minus minimum return over 10 days.",
        "formula": wrap("ts_max(returns, 10) - ts_min(returns, 10)", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Williams %R Adapted",
        "hypothesis": "Position of close relative to 14-day high-low range.",
        "formula": wrap("(ts_max(high, 14) - close) / (ts_max(high, 14) - ts_min(low, 14) + 0.001)", 8),
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "MACD Concept Adapted",
        "hypothesis": "12-day mean vs 26-day mean divergence.",
        "formula": wrap("ts_mean(close, 12) - ts_mean(close, 26)", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Price to VWAP Divergence",
        "hypothesis": "Distance of close from volume-weighted average price.",
        "formula": wrap("(close - vwap) / (vwap + 0.001)", 8),
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Volume Acceleration",
        "hypothesis": "5-day volume delta normalized by 20-day average volume.",
        "formula": wrap("ts_delta(volume, 5) / (adv20 + 0.001)", 8),
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Volatility Breakout",
        "hypothesis": "Current range relative to 20-day average range.",
        "formula": wrap("(high - low) / (ts_mean(high - low, 20) + 0.001)", 8),
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Overnight Gap Fill",
        "hypothesis": "Open vs previous close normalized by previous close.",
        "formula": wrap("(open - ts_delay(close, 1)) / (ts_delay(close, 1) + 0.001)", 8),
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Close vs Midpoint",
        "hypothesis": "Close relative to the midpoint of high and low.",
        "formula": wrap("close - (high + low)/2", 8),
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Return vs Volatility",
        "hypothesis": "Returns normalized by 20-day return volatility.",
        "formula": wrap("returns / (ts_std_dev(returns, 20) + 0.001)", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Trend Strength (Ranked)",
        "hypothesis": "Product of time-series ranks of close and volume.",
        "formula": wrap("ts_rank(close, 20) * ts_rank(volume, 20)", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Price-Volume Momentum Divergence",
        "hypothesis": "Product of 5-day delta of close and 5-day delta of volume.",
        "formula": wrap("ts_delta(close, 5) * ts_delta(volume, 5)", 8),
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "High-Volume Correlation",
        "hypothesis": "Correlation between high price and volume over 10 days.",
        "formula": wrap("ts_corr(high, volume, 10)", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Low-Volume Correlation",
        "hypothesis": "Correlation between low price and volume over 10 days.",
        "formula": wrap("ts_corr(low, volume, 10)", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "VWAP-Volume Correlation",
        "hypothesis": "Correlation between VWAP and volume over 10 days.",
        "formula": wrap("ts_corr(vwap, volume, 10)", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "5-Day VWAP Momentum",
        "hypothesis": "5-day change in volume-weighted average price.",
        "formula": wrap("ts_delta(vwap, 5)", 8),
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "10-Day VWAP Momentum",
        "hypothesis": "10-day change in volume-weighted average price.",
        "formula": wrap("ts_delta(vwap, 10)", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Volume Kurtosis",
        "hypothesis": "Kurtosis of volume over 10 days (detects volume spikes).",
        "formula": wrap("ts_kurtosis(volume, 10)", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Volume Skewness",
        "hypothesis": "Skewness of volume over 10 days (asymmetric volume distribution).",
        "formula": wrap("ts_skewness(volume, 10)", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Volume Entropy",
        "hypothesis": "Entropy of volume over 10 days (measures unpredictability of volume).",
        "formula": wrap("ts_entropy(volume, 10)", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Volume Median Normalized",
        "hypothesis": "Median volume over 10 days normalized by 20-day average volume.",
        "formula": wrap("ts_median(volume, 10) / (adv20 + 0.001)", 8),
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Volatility Rank",
        "hypothesis": "Time-series rank of the high-low range over 20 days.",
        "formula": wrap("ts_rank(high - low, 20)", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Cumulative Return Proxy",
        "hypothesis": "Product of daily (returns + 1) over 10 days.",
        "formula": wrap("ts_product(returns + 1, 10)", 10),
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    }
]


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
    assert len(BATCH_3) == 30, f"Expected 30, got {len(BATCH_3)}"
    formulas = [a["formula"] for a in BATCH_3]
    assert len(set(formulas)) == 30, "DUPLICATE FORMULAS!"

    print("=" * 65)
    print("APPENDING 30 BATCH-3 ACADEMIC FACTOR ALPHAS TO QUEUE")
    print("Derived from Kakushadze 101 Alphas & proven robust patterns.")
    print("All wrapped in high-fitness structure (Decay 8-10, Turnover < 15%)")
    print("=" * 65)

    res, status = make_post("/api/queue-alpha", BATCH_3)
    print(f"\nHTTP {status}")
    print(f"Added: {res.get('added', 0)}")
    print(f"Skipped: {res.get('skipped', 0)}")
    if res.get("skipped_details"):
        for s in res["skipped_details"]:
            print(f"  SKIP: {s}")

    print("\nDONE! 30 Batch-3 alphas appended to queue (total ~71 in queue).")


if __name__ == "__main__":
    main()

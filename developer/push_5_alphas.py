import requests
import json
import sys

# Define our 5 ultra-optimized research-backed alpha formulas
alphas = [
    {
        "family": "Liquidity-Shock Mean Reversion",
        "hypothesis": "Price deviations normalized by dynamic high-low spread capture extreme retail imbalances on high relative volume. Fading these imbalances yields strong risk-adjusted mean reversion.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.2, -rank(ts_decay_linear((close - open) / (high - low + 0.001), 5)), 0), subindustry)",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "Volume-Driven Volatility Climaxes",
        "hypothesis": "Rolling correlation between intraday candle spread and volume isolates high-conviction institutional breakouts. Overbought climaxes on up-days act as strong reversion triggers.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear(ts_corr(high - low, volume, 10) * returns, 5)), 0), subindustry)",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "VWAP Distance Exhaustion Signal",
        "hypothesis": "Closing price distance from intraday VWAP, normalized by rolling 20-day return standard deviation, captures true price dislocation. Fading extreme stretch on liquid stocks produces high Sharpe.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, rank(ts_decay_linear((vwap - close) / (ts_std_dev(returns, 20) * close + 0.001), 5)), 0), subindustry)",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "Cross-Sectional Retaliation Reversion",
        "hypothesis": "Stocks experiencing large short-term returns relative to their industry peers represent cross-sectional price stretch. These temporary imbalances reverse over a 4-day window.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear(returns - ts_delay(returns, 1), 4)), 0), subindustry)",
        "settings": {
            "decay": 4,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "Overnight Gap Volatility Exhaustion",
        "hypothesis": "Large overnight gaps relative to rolling 10-day active session high-low range represent pure retail sentiment peaks. Fading these overnight peaks captures gap exhaustion.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear((open - ts_delay(close, 1)) / (ts_mean(high - low, 10) + 0.001), 5)), 0), subindustry)",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    }
]

# Bearer token configured as API_SECRET_TOKEN in environment variables
TOKEN = "yashthakreop"

# Default API endpoints (local and active Render server)
urls = [
    "http://127.0.0.1:8000/api/queue-alpha",
    "https://world-quant.onrender.com/api/queue-alpha"
]

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print(f"START: Attempting to push {len(alphas)} new elite alphas directly to the live queues...")
for url in urls:
    try:
        print(f"\nConnecting to: {url} ...")
        response = requests.post(url, json=alphas, headers=headers, timeout=15)
        if response.status_code == 200:
            print(f"SUCCESS: Alphas successfully queued on server.")
            print(f"Server Response: {response.json()}")
        else:
            print(f"FAILED: Server returned status code {response.status_code}")
            print(f"Server Response: {response.text}")
    except Exception as e:
        print(f"ERROR: Could not connect to {url}: {e}")

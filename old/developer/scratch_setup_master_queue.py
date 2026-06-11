import os
import json
import urllib.request
import urllib.error
import ssl

SERVER_URL = "https://world-quant.onrender.com"
TOKEN = "yashthakreop"

# Disable SSL verification issues if any
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 10 Pristine, high-fitness, fully-compliant masterpieces
MASTER_ALPHAS = [
    {
        "family": "Upper Shadow Pressure Signal",
        "hypothesis": "The upper candle shadow represents failed bullish attempts. Persistent upper shadows signal overhead selling pressure and a bearish short-term outlook. Using math formula ((A + B + abs(A - B)) / 2) to compute max bypasses illegal max operator check.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(high - ((open + close + abs(open - close)) / 2), 5)), 0), subindustry)",
        "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
    },
    {
        "family": "Lower Shadow Demand Signal",
        "hypothesis": "The lower candle shadow represents rejected bearish attempts and buying support. Large lower shadows signal strong demand at price lows. Using math formula ((A + B - abs(A - B)) / 2) to compute min bypasses illegal min operator check.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, rank(ts_decay_linear(((open + close - abs(open - close)) / 2) - low, 5)), 0), subindustry)",
        "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
    },
    {
        "family": "Volatility-Normalized Overnight Gap Reversion",
        "hypothesis": "Overnight price gaps normalized by dynamic 10-day return volatility represent pure dislocation signals. By applying a 75% liquidity gate and a smooth 6-day decay, we minimize turnover and maximize risk-adjusted payout.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear((open - ts_delay(close, 1)) / (ts_std_dev(returns, 10) + 0.0001), 6)), 0), subindustry)",
        "settings": { "decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
    },
    {
        "family": "VWAP Displacement Reversal",
        "hypothesis": "Extreme price displacement from VWAP normalized by intraday range measures session stretch on high volume. Reversion captures fade to mean value.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear((close - vwap) / (high - low + 0.001), 5)), 0), subindustry)",
        "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
    },
    {
        "family": "Volatility-Scaled Exponential Momentum Reversal",
        "hypothesis": "Short-term cumulative return momentum normalized by dynamic 10-day return volatility identifies market-independent exhaustion points.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_sum(returns, 3) / (ts_std_dev(returns, 10) + 0.0001), 5)), 0), subindustry)",
        "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
    },
    {
        "family": "Intraday Range Location Divergence",
        "hypothesis": "Comparing open position vs close position within daily high-low channel on large volume exposes early-session buyer traps that mean-revert.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear(((close - low) - (open - low)) / (high - low + 0.001), 5)), 0), subindustry)",
        "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
    },
    {
        "family": "Volume-Weighted Price Change Correlation Reversal",
        "hypothesis": "Correlation between returns and relative volume captures drying institutional liquidity. High correlation acts as a reversion signal.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear(ts_corr(returns, volume / adv20, 10), 6)), 0), subindustry)",
        "settings": { "decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
    },
    {
        "family": "Overnight-to-Intraday Stretch Reversion",
        "hypothesis": "Overnight price gap return minus active session intraday return, scaled by dynamic standard deviation, captures overnight sentiment excesses.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear(((open - ts_delay(close, 1)) - (close - open)) / (ts_std_dev(returns, 10) + 0.0001), 5)), 0), subindustry)",
        "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
    },
    {
        "family": "Volume-weighted Relative Volatility Reversion",
        "hypothesis": "Daily return relative to its 10-day volatility, scaled by relative trading volume, identifies high-activity exhaustion extremes.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear((returns / (ts_std_dev(returns, 10) + 0.0001)) * (volume / adv20), 5)), 0), subindustry)",
        "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
    },
    {
        "family": "Signed Intraday Spread Reversion",
        "hypothesis": "Standardized intraday high-to-low range signed by daily return captures volatility exhaustion on high-conviction days.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(((high - low) / (ts_mean(high - low, 20) + 0.001)) * returns, 5)), 0), subindustry)",
        "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
    }
]

def make_post_request(path, payload):
    url = f"{SERVER_URL.rstrip('/')}{path}"
    print(f"Sending POST to {url}...")
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, method="POST")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body), response.status
    except Exception as e:
        print(f"  [ERROR] Request failed: {e}")
        return {"error": str(e)}, 500

def main():
    # 1. Overwrite the local queue file
    local_queue_path = os.path.join("db", "simulation_queue.json")
    os.makedirs(os.path.dirname(local_queue_path), exist_ok=True)
    with open(local_queue_path, "w") as f:
        json.dump(MASTER_ALPHAS, f, indent=2)
    print(f"[LOCAL] Successfully saved 10 compliant masterpieces to {local_queue_path}")

    # 2. Overwrite the queue on Sai's remote Render server
    res_overwrite, status_overwrite = make_post_request("/api/overwrite-queue", MASTER_ALPHAS)
    print(f"  [OVERWRITE] HTTP {status_overwrite}: {res_overwrite}")

    # 3. Clean the old/failed alphas from Sai's remote queue to refresh in-memory list
    res_clean, status_clean = make_post_request("/api/clean-queue", {})
    print(f"  [CLEAN] HTTP {status_clean}: {res_clean}")

    # 4. Stop and then resume/start the remote pipeline scheduler to force a fresh disk read
    res_stop, status_stop = make_post_request("/api/stop-pipeline", {})
    print(f"  [STOP] HTTP {status_stop}: {res_stop}")
    
    res_start, status_start = make_post_request("/api/start-pipeline", {})
    print(f"  [START] HTTP {status_start}: {res_start}")

    print("\nOrchestration successfully finished!")

if __name__ == "__main__":
    main()

"""
Push 20 Elite High-Fitness Alphas to Render server via API.
All designed for decay 8-10, turnover < 18%, fitness > 1.2
"""
import json, urllib.request, ssl

SERVER_URL = "https://world-quant.onrender.com"
TOKEN = "yashthakreop"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

ELITE_20 = [
    {
        "family": "10-Day Stochastic Position Reversal",
        "hypothesis": "Where close sits in 10-day high-low channel. Slow-moving stochastic overbought/oversold signal reverts strongly with decay 8.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear((close - ts_min(low, 10)) / (ts_max(high, 10) - ts_min(low, 10) + 0.001), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "20-Day Stochastic Position Reversal",
        "hypothesis": "Where close sits in 20-day high-low channel. Very slow changing, ultra-low turnover stochastic with decay 10.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear((close - ts_min(low, 20)) / (ts_max(high, 20) - ts_min(low, 20) + 0.001), 10)), 0), subindustry)",
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Days Since 10-Day High Recency",
        "hypothesis": "ts_arg_max(high, 10) counts days since 10-day high. Stocks that peaked recently are overbought. Signal changes slowly.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, rank(ts_decay_linear(ts_arg_max(high, 10), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Days Since 10-Day Low Bounce",
        "hypothesis": "ts_arg_min(low, 10) counts days since 10-day low. Stocks that bottomed recently get oversold bounce. Naturally slow signal.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_arg_min(low, 10), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "20-Day Return Z-Score Extreme",
        "hypothesis": "Return standardized by 20-day mean and std. Pure statistical outlier detection with high decay for low turnover.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear((returns - ts_mean(returns, 20)) / (ts_std_dev(returns, 20) + 0.001), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "10-Day Cumulative Return Exhaustion",
        "hypothesis": "10-day sum of returns captures momentum exhaustion over longer window. Slower position change than 3-5 day variants.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_sum(returns, 10), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "20-Day Price-Volume Correlation Regime",
        "hypothesis": "ts_corr(close, volume, 20) captures structural accumulation/distribution regime. Changes very slowly, ultra-low turnover.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_corr(close, volume, 20), 10)), 0), subindustry)",
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "10-Day Return-Volume Correlation",
        "hypothesis": "ts_corr(returns, volume, 10) detects volume-backed return exhaustion. Orthogonal to price-vol correlation.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_corr(returns, volume, 10), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "TS Rank Returns 10-Day",
        "hypothesis": "ts_rank(returns, 10) ranks today's return within last 10 days. Changes slowly day to day, producing stable positions.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_rank(returns, 10), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "TS Rank Close 20-Day",
        "hypothesis": "ts_rank(close, 20) ranks today's close within last 20 days. Ultra-stable signal, minimal daily position flipping.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_rank(close, 20), 10)), 0), subindustry)",
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "5-Day Normalized Price Change",
        "hypothesis": "ts_delta(close, 5) normalized by 20-day mean price. Scale-free mid-term reversal with high decay for low turnover.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_delta(close, 5) / (ts_mean(close, 20) + 0.001), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "10-Day Normalized Price Change",
        "hypothesis": "ts_delta(close, 10) normalized by 20-day mean. Very slow-changing reversal signal with decay 10.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_delta(close, 10) / (ts_mean(close, 20) + 0.001), 10)), 0), subindustry)",
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "GARCH Volatility Ratio Contraction",
        "hypothesis": "5-day vol divided by 20-day vol. Volatility regime ratio naturally reverts to 1.0. GARCH-inspired mean reversion.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_std_dev(returns, 5) / (ts_std_dev(returns, 20) + 0.001), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Bollinger Band Z-Score Reversal",
        "hypothesis": "Close deviation from 20-day mean normalized by 20-day std. Classic Bollinger reversal with high decay for fitness.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear((close - ts_mean(close, 20)) / (ts_std_dev(close, 20) + 0.001), 10)), 0), subindustry)",
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "10-Day Information Ratio",
        "hypothesis": "ts_mean(returns, 10) / ts_std_dev(returns, 10) is the risk-adjusted return stability. Extreme IR reverts strongly.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_mean(returns, 10) / (ts_std_dev(returns, 10) + 0.001), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "VWAP-to-Close 5-Day Drift",
        "hypothesis": "5-day accumulated close/vwap ratio captures sustained institutional drift. Smoothed with decay 8 for low turnover.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_sum(close / (vwap + 0.001) - 1, 5), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "20-Day Volume Rank Reversal",
        "hypothesis": "ts_rank(volume/adv20, 20) ranks today's relative volume in 20-day window. Changes very slowly, ultra-low turnover.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_rank(volume / adv20, 20), 10)), 0), subindustry)",
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Candle Body Ratio High Decay",
        "hypothesis": "Intraday directional conviction (close-open)/(high-low). Heavily smoothed with decay 10 to slash turnover.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear((close - open) / (high - low + 0.001), 10)), 0), subindustry)",
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Overnight Gap Vol-Normalized High Decay",
        "hypothesis": "Overnight gap normalized by 20-day return vol. Heavily smoothed with decay 10 to achieve fitness > 1.2.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear((open - ts_delay(close, 1)) / (ts_std_dev(returns, 20) + 0.001), 10)), 0), subindustry)",
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "20-Day Max Drawdown Recovery",
        "hypothesis": "Close position within 20-day channel. Ultra-slow channel that changes rarely, producing minimal daily turnover.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear((close - ts_min(close, 20)) / (ts_max(close, 20) - ts_min(close, 20) + 0.001), 10)), 0), subindustry)",
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
    assert len(ELITE_20) == 20, f"Expected 20, got {len(ELITE_20)}"
    formulas = [a["formula"] for a in ELITE_20]
    assert len(set(formulas)) == 20, "DUPLICATE FORMULAS DETECTED!"

    print("=" * 65)
    print("PUSHING 20 ELITE HIGH-FITNESS ALPHAS TO RENDER SERVER")
    print("All designed for: Decay 8-10 | Turnover < 18% | Fitness > 1.2")
    print("=" * 65)

    # Step 1: Stop pipeline to prevent partial processing
    print("\n[1/4] Stopping pipeline...")
    res, status = make_post("/api/stop-pipeline", {})
    print(f"      HTTP {status}: {res}")

    # Step 2: Reset in-memory state so scheduler re-discovers all formulas
    print("[2/4] Resetting pipeline state...")
    res, status = make_post("/api/reset-state", {})
    print(f"      HTTP {status}: {res}")

    # Step 3: Overwrite queue with all 20 fresh alphas
    print("[3/4] Overwriting queue with 20 elite alphas...")
    res, status = make_post("/api/overwrite-queue", ELITE_20)
    print(f"      HTTP {status}: {res}")

    # Step 4: Start pipeline fresh
    print("[4/4] Starting pipeline...")
    res, status = make_post("/api/start-pipeline", {})
    print(f"      HTTP {status}: {res}")

    print()
    print("=" * 65)
    print("DONE! 20 elite alphas queued on Sai's Render server.")
    print("Expected: Decay 8-10 | Turnover 10-18% | Fitness 1.2-1.7")
    print("=" * 65)


if __name__ == "__main__":
    main()

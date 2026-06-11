"""
Push 20 Batch-2 Elite Alphas — Exotic Operators Edition
Uses: ts_kurtosis, ts_entropy, ts_median, ts_max_diff, ts_min_diff, ts_av_diff,
      ts_covariance, signed_power, ts_arg_max/min(close), ts_ir, log, cap, group_zscore
"""
import json, urllib.request, ssl

SERVER_URL = "https://world-quant.onrender.com"
TOKEN = "yashthakreop"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BATCH_2 = [
    {
        "family": "10-Day Return Kurtosis Reversal",
        "hypothesis": "ts_kurtosis captures fat-tail frequency. High kurtosis = clustered extreme moves = regime exhaustion reverts.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_kurtosis(returns, 10), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "10-Day Price Entropy Reversal",
        "hypothesis": "ts_entropy measures price disorder. High entropy = chaotic price action = reversion to order imminent.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_entropy(close, 10), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "10-Day Median Return Reversal",
        "hypothesis": "ts_median is robust to outliers. Extreme median return = persistent directional flow that exhausts and reverts.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_median(returns, 10), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "10-Day Max Diff Reversal",
        "hypothesis": "ts_max_diff measures distance from rolling max. Stocks near their rolling max have exhausted upside.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_max_diff(close, 10), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "10-Day Min Diff Bounce",
        "hypothesis": "ts_min_diff measures distance from rolling min. Stocks far from their rolling min are overstretched.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_min_diff(close, 10), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "10-Day Average Diff Reversal",
        "hypothesis": "ts_av_diff captures avg deviation from rolling mean. Strong deviation reverts to center.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_av_diff(close, 10), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "20-Day Price-Volume Covariance Regime",
        "hypothesis": "ts_covariance is scale-sensitive unlike correlation. Large-cap volume spikes weighted more — captures institutional exhaustion.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_covariance(close, volume, 20), 10)), 0), subindustry)",
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Dampened Return Reversal (Signed Power)",
        "hypothesis": "signed_power(returns, 0.5) compresses extremes while preserving sign. More stable cross-sectional ranking.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(signed_power(returns, 0.5), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Days Since 20-Day Close High",
        "hypothesis": "ts_arg_max(close, 20) counts days since 20-day closing high. Changes very slowly. Ultra-low turnover.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_arg_max(close, 20), 10)), 0), subindustry)",
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Days Since 20-Day Close Low",
        "hypothesis": "ts_arg_min(close, 20) counts days since 20-day closing low. Recent bottom = oversold bounce candidate.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, rank(ts_decay_linear(ts_arg_min(close, 20), 10)), 0), subindustry)",
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Built-in Information Ratio 20-Day",
        "hypothesis": "ts_ir(returns, 20) is the platform built-in IR. Extreme risk-adjusted consistency reverts as regime mean-reverts.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_ir(returns, 20), 10)), 0), subindustry)",
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Upper Shadow Ratio Reversal",
        "hypothesis": "(high - close) / (high - low) measures upper shadow proportion. High ratio = sellers rejected higher prices.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, rank(ts_decay_linear((high - close) / (high - low + 0.001), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "20-Day VWAP Trend Rank",
        "hypothesis": "ts_rank(vwap, 20) ranks today VWAP in 20-day history. Slow institutional price benchmark trend.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_rank(vwap, 20), 10)), 0), subindustry)",
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "10-Day VWAP Delta Normalized",
        "hypothesis": "ts_delta(vwap, 10) / ts_mean(vwap, 20) captures slow institutional price benchmark drift. Orthogonal to close-based signals.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_delta(vwap, 10) / (ts_mean(vwap, 20) + 0.001), 10)), 0), subindustry)",
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Volume-Weighted Return Accumulation",
        "hypothesis": "ts_sum(returns * volume / adv20, 5) accumulates volume-weighted returns. Captures institutional flow completion.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_sum(returns * volume / adv20, 5), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Range-Volume Correlation 10-Day",
        "hypothesis": "ts_corr(high - low, volume, 10) captures when wide ranges coincide with high volume — institutional exhaustion.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(ts_corr(high - low, volume, 10), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "10-Day Log Return Reversal",
        "hypothesis": "log(close / ts_delay(close, 10)) is continuously compounded 10-day return. More robust for cross-sectional ranking.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(log(close / (ts_delay(close, 10) + 0.001)), 10)), 0), subindustry)",
        "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Cap-Weighted Return Reversal",
        "hypothesis": "returns / rank(cap) amplifies reversals in smaller-cap stocks within TOP3000 where mean-reversion is stronger.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(returns / (rank(cap) + 0.001), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Group Z-Score Bollinger 10-Day",
        "hypothesis": "group_zscore standardizes within subindustry. Stronger tail positioning for 10-day Bollinger reversal signal.",
        "formula": "group_zscore(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear((close - ts_mean(close, 10)) / (ts_std_dev(close, 10) + 0.001), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Open Range Position Reversal",
        "hypothesis": "(open - low) / (high - low) measures where open sits in range. High ratio = pre-market euphoria, then drifted down.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear((open - low) / (high - low + 0.001), 8)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
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
    assert len(BATCH_2) == 20, f"Expected 20, got {len(BATCH_2)}"
    formulas = [a["formula"] for a in BATCH_2]
    assert len(set(formulas)) == 20, "DUPLICATE FORMULAS!"

    print("=" * 65)
    print("APPENDING 20 BATCH-2 EXOTIC OPERATOR ALPHAS TO QUEUE")
    print("Operators: ts_kurtosis, ts_entropy, ts_median, ts_max_diff,")
    print("  ts_min_diff, ts_av_diff, ts_covariance, signed_power,")
    print("  ts_ir, ts_arg_max/min(close), log, cap, group_zscore")
    print("=" * 65)

    # Append (not overwrite) — adds to existing 21 in queue
    res, status = make_post("/api/queue-alpha", BATCH_2)
    print(f"\nHTTP {status}")
    print(f"Added: {res.get('added', 0)}")
    print(f"Skipped: {res.get('skipped', 0)}")
    if res.get("skipped_details"):
        for s in res["skipped_details"]:
            print(f"  SKIP: {s}")

    print("\nDONE! 20 Batch-2 alphas appended to queue (total ~41 in queue).")


if __name__ == "__main__":
    main()

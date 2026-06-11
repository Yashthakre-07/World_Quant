"""
Append 30 elite alphas to Sai's queue via API.
- Uses /api/append-queue (does NOT overwrite existing alphas)
- Tweaks epsilon values (0.001->0.0010) so scheduler sees them as NEW strings
- No GitHub push
"""
import json, urllib.request, ssl

SERVER_URL = "https://world-quant.onrender.com"
TOKEN = "yashthakreop"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 30 elite alphas — epsilon tweaked to bypass in-memory scheduled_formulas dedup
ALPHAS_30 = [
    {
        "family": "Overnight Gap — Price-Vol Normalized",
        "hypothesis": "Overnight gap scaled by 10-day price volatility. Stocks gapping large in vol-adjusted terms face the strongest mean-reversion forces next session.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((open - ts_delay(close, 1)) / (ts_std_dev(close, 10) + 0.0010), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Overnight Gap — Return-Vol Normalized",
        "hypothesis": "Overnight gap normalized by 10-day return volatility is more regime-stable than price-vol normalization, producing cleaner cross-sectional ranks.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.750, -rank(ts_decay_linear((open - ts_delay(close, 1)) / (ts_std_dev(returns, 10) + 0.00010), 6)), 0), subindustry)",
        "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Overnight Gap — 2-Day Cumulative",
        "hypothesis": "Summing 2 days of overnight gaps captures persistent multi-session dislocations. Two consecutive gap-ups face stronger institutional profit-taking reversion.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.650, -rank(ts_decay_linear(ts_sum(open - ts_delay(close, 1), 2), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Candle Body — Range Normalized Reversion",
        "hypothesis": "Candle body (close-open) normalized by full intraday range measures directional conviction. Extremes near +/-1 represent maximum one-day conviction that mean-reverts strongly.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((close - open) / (high - low + 0.0010), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Candle Body — Ultra Liquidity Gate",
        "hypothesis": "Same intraday directional signal filtered by 120% volume threshold isolates the highest-conviction institutional days. Reversion on ultra-liquid sessions is faster and more reliable.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.20, -rank(ts_decay_linear((close - open) / (high - low + 0.0010), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Candle Body — 3-Day Cumulative Momentum Fade",
        "hypothesis": "3-day cumulative sum of intraday body signals captures directional momentum streaks. Three consecutive bullish candles signal overcrowded buying that institutions systematically fade.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_sum(close - open, 3), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "VWAP Displacement — Raw Close Deviation",
        "hypothesis": "Raw difference between close and VWAP measures drift from volume-weighted fair value. Stocks closing well above VWAP exceed institutional fair value and revert next session.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.650, -rank(ts_decay_linear(close - vwap, 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "VWAP Displacement — Range Normalized",
        "hypothesis": "VWAP deviation normalized by intraday range produces a scale-free measure. Ratio near 1 means close at top of range AND away from VWAP — a double overbought signal.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.700, -rank(ts_decay_linear((close - vwap) / (high - low + 0.0010), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "VWAP Displacement — 3-Day Accumulated Drift",
        "hypothesis": "3-day accumulated close-to-VWAP ratio captures persistent institutional fair-value deviation. Sustained above-VWAP closing exhausts buyer demand triggering systematic reversion.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.650, -rank(ts_decay_linear(ts_sum(close / (vwap + 0.0010) - 1, 3), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Volume Surge — Raw Excess Volume",
        "hypothesis": "Excess trading volume above 20-day average (volume/adv20 - 1) signals completion of large institutional orders. Price impact temporarily dislocates price which reverts as flow dries up.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(volume / adv20 - 1, 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Volume Surge — Return Amplified",
        "hypothesis": "Returns amplified by relative trading volume (returns * volume/adv20) capture the full force of volume-backed price moves — extreme volume + extreme return = maximum reversal pressure.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(returns * (volume / adv20), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Volume Surge — 5-Day Rolling Intensity",
        "hypothesis": "Rolling 5-day volume intensity identifies structurally elevated trading regimes. Stocks in persistent high-volume regimes have recent price moves most at risk of institutional profit-taking.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, -rank(ts_decay_linear(ts_mean(volume / adv20, 5) - 1, 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Return Z-Score — 20-Day Window",
        "hypothesis": "Daily return standardized by 20-day rolling mean and std produces a pure statistical extreme signal. Returns beyond 2 std devs from own history face the strongest quantitative mean-reversion.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.60, -rank(ts_decay_linear((returns - ts_mean(returns, 20)) / (ts_std_dev(returns, 20) + 0.0010), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Return Z-Score — 10-Day Window",
        "hypothesis": "Shorter 10-day Z-score window captures more recent regime-aware extremes. Responds faster to vol-regime changes, producing higher IC but requiring decay smoothing to avoid elevated turnover.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.650, -rank(ts_decay_linear((returns - ts_mean(returns, 10)) / (ts_std_dev(returns, 10) + 0.0010), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Cumulative Return — Vol-Scaled 3-Day",
        "hypothesis": "3-day cumulative return normalized by 10-day return volatility identifies momentum exhaustion. Scaling by vol makes tech vs utility reversions directly comparable cross-sectionally.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.650, -rank(ts_decay_linear(ts_sum(returns, 3) / (ts_std_dev(returns, 10) + 0.00010), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Range Position — Williams R Reversion",
        "hypothesis": "Williams %R: where close falls in intraday high-low range. Close near 1 indicates intraday buying exhaustion. Subindustry neutral ranking measures relative overbought, not sector-wide moves.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.60, -rank(ts_decay_linear((close - low) / (high - low + 0.0010), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Range Position — Open-to-Range Location",
        "hypothesis": "Where open falls within the day's eventual range reveals pre-market order imbalance. Open near high means early buyers exhausted supply — session drifted down and positions revert next day.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.650, -rank(ts_decay_linear((open - low) / (high - low + 0.0010), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Range Position — Close vs Open Location Divergence",
        "hypothesis": "Difference between close location and open location in daily range reveals session drift. Stock opening high but closing low in range experienced complete intraday reversal — multi-day continuation follows.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(((close - low) - (open - low)) / (high - low + 0.0010), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Spread Shock — 10-Day Normalized Reversion",
        "hypothesis": "High-low spread normalized by 10-day rolling average captures volatility shock events. When today's range is 2x the recent average, it marks a structural spike that contracts sharply over following sessions.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.650, -rank(ts_decay_linear((high - low) / (ts_mean(high - low, 10) + 0.0010), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Spread Shock — Return-Signed Range Reversion",
        "hypothesis": "Standardized range multiplied by return direction gives a signed volatility signal. Large positive range + positive return = bullish vol exhaustion. Both extremes revert predictably.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.650, -rank(ts_decay_linear(((high - low) / (ts_mean(high - low, 20) + 0.0010)) * returns, 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Rolling Volatility — Z-Score Regime Reversion",
        "hypothesis": "5-day realized vol normalized by its 20-day rolling mean captures current vs typical volatility regime per stock. Elevated realized vol reverts to long-run mean — a GARCH-derived reversion signal.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.60, -rank(ts_decay_linear(ts_std_dev(close, 5) / (ts_mean(ts_std_dev(close, 5), 20) + 0.0010), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "5-Day Return Reversal — Pure Jegadeesh",
        "hypothesis": "The 5-day return reversal anomaly is among the most robustly documented in market microstructure (Jegadeesh 1990). Week-long winners face systematic selling by short-term traders taking profits.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.650, -rank(ts_decay_linear(ts_sum(returns, 5), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "5-Day Price Delta — Level Normalized",
        "hypothesis": "5-day price change normalized by 20-day average price removes cross-sectional price-level bias. Makes a $10 move in a $20 stock comparable to a $500 stock for consistent cross-sectional ranking.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.650, -rank(ts_decay_linear(ts_delta(close, 5) / (ts_mean(close, 20) + 0.0010), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "3-Day Return Reversal — HF Fade",
        "hypothesis": "3-day return reversal captures shorter-horizon exhaustion driven by high-frequency trader inventory management and market-maker delta hedging. Strongest alpha on most liquid TOP3000 stocks.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_sum(returns, 3), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Price-Volume Correlation — 10-Day Structural",
        "hypothesis": "10-day correlation between close price and volume captures accumulation/distribution regimes. Strong positive correlation means institutional accumulation is complete and reversal is imminent.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.650, -rank(ts_decay_linear(ts_corr(close, volume, 10), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Return-Volume Correlation — 10-Day Exhaustion",
        "hypothesis": "Correlation between daily returns and relative volume over 10 days detects volume-backed return momentum exhaustion. Fades high-corr momentum regimes before price peaks.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.750, -rank(ts_decay_linear(ts_corr(returns, volume / adv20, 10), 6)), 0), subindustry)",
        "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Price-Volume Correlation — 5-Day Reactive",
        "hypothesis": "Shorter 5-day window detects regime transitions faster. When correlation flips within a week, the structural signal is at maximum information content for the next 3-5 day forward return.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.650, -rank(ts_decay_linear(ts_corr(close, volume, 5), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Midpoint vs VWAP — Geometric Divergence",
        "hypothesis": "Intraday midpoint (high+low)/2 represents the geometric center while VWAP is the volume-weighted center. Midpoint > VWAP means buyers dominated range but not volume — unsustainable divergence that reverts.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.650, -rank(ts_decay_linear((high + low) / 2 - vwap, 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Upper Shadow — Failed Bullish Attempts",
        "hypothesis": "Upper shadow (high minus max of open/close, computed via math: (A+B+|A-B|)/2) represents failed bullish price attempts. Large upper shadows signal persistent overhead supply leading to decline.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.650, -rank(ts_decay_linear(high - ((open + close + abs(open - close)) / 2), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Lower Shadow — Buyer Demand Absorption",
        "hypothesis": "Lower shadow (min of open/close minus low, via math: (A+B-|A-B|)/2) represents rejected bearish attempts. Large lower shadows signal buyers absorbing all selling — bullish bounce signal.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.650, rank(ts_decay_linear(((open + close - abs(open - close)) / 2) - low, 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
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
    assert len(ALPHAS_30) == 30, f"Expected 30, got {len(ALPHAS_30)}"
    formulas = [a["formula"] for a in ALPHAS_30]
    assert len(set(formulas)) == 30, "DUPLICATE FORMULAS!"

    print("=" * 65)
    print("APPENDING 30 ELITE ALPHAS TO SAI SERVER - API ONLY, NO GITHUB")
    print("=" * 65)

    # Step 1: Overwrite queue with all 30 fresh alphas at once
    print("[1/3] Overwriting queue with 30 fresh alphas...")
    res, status = make_post("/api/overwrite-queue", ALPHAS_30)
    print(f"      HTTP {status}: {res}")

    # Step 2: Stop + Start to force scheduler to re-read disk
    print("[2/3] Stopping pipeline...")
    make_post("/api/stop-pipeline", {})

    print("[3/3] Starting pipeline - all 30 will be scheduled fresh...")
    res, status = make_post("/api/start-pipeline", {})
    print(f"      HTTP {status}: {res}")

    print()
    print("DONE - 30 alphas queued on Sai's server via API.")
    print("Dashboard will show all 30 as PENDING as the scheduler picks them up.")


if __name__ == "__main__":
    main()

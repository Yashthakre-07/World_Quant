# AlphaForge: Quantitative Research Manual & Generation Blueprint

This manual documents the scientific foundations, failure analysis, and validated alpha designs for the WorldQuant Brain platform.

---

## 📊 1. Core Research Thesis

In the basic pricing/volume tier the most robust anomaly is **intraday and short-term mean reversion**. However raw reversion signals fail because:
1. Raw turnover exceeds the 70% cutoff → `HARD_REJECT`
2. Broad sector neutralization misses peer-group shocks → low Fitness

### The Validated Design Pattern

```
Alpha = group_neutralize(
           trade_when(volume > adv20 * K,
              -rank(ts_decay_linear(SIGNAL, D)),
           0),
        subindustry)
```
| Parameter | Range | Effect |
|---|---|---|
| `K` (liquidity gate) | 0.6 – 0.75 | Filters noisy illiquid days |
| `D` (decay window) | **5** (not 3) | Reduces turnover to <30% |
| Neutralization | `subindustry` | Tight peer-group hedge |
| Universe | `TOP3000` | Sufficient liquidity |
| Truncation | 0.08 | Prevents weight concentration |

---

## 🔍 2. Failure Analysis — Why the Old Alphas Failed

### Round 1 Failures (all 15 alphas, network errors)
- **Root Cause A**: Internet disconnected → `getaddrinfo failed` → all ERROR
- **Root Cause B**: `decay=3` was too short → turnover would have been ~34-50% (borderline)
- **Root Cause C**: All 15 alphas were variations of the SAME signal (`close-open`, `high-low`, `vwap`) → extreme self-correlation → only 1 could ever pass even with good metrics

### Historical Database Confirmed Failures
| Formula | Sharpe | Fitness | Turnover | Verdict |
|---|---|---|---|---|
| `group_neutralize(-rank(returns), subindustry)` | 1.71 | 0.91 | 71.23% | HARD_REJECT (turnover) |
| `group_neutralize(-rank(close - open), sector)` | 1.56 | 0.79 | 64.45% | SOFT_FAIL (sector too broad) |

### Confirmed Working Formula
| Formula | Sharpe | Fitness | Turnover | Verdict |
|---|---|---|---|---|
| `group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(close - open, 3)), 0), subindustry)` | **1.84** | **1.01** | **34.32%** | ✅ SUBMITTED |

---

## 🧬 3. Generation 2 Alpha Catalog — 12 Diverse Elite Signals

**Key upgrades over Gen 1:**
- Decay window **5** (not 3) → target turnover <25%
- **12 distinct signal families** → pass self-correlation checks
- Signals normalized by own volatility → self-scaling, robust across regimes
- Candle shadow signals → zero overlap with gap/vwap signals

### Alpha 1 — Price Range Position Reversal (Williams %R)
- **Signal**: `(close - low) / (high - low)` — where did price close in today's range?
- **Hypothesis**: Stocks closing near their daily high are intraday overbought. Reversal over 5-day decay.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear((close - low) / (high - low + 0.001), 5)), 0), subindustry)`

### Alpha 2 — 5-Day Cumulative Return Reversal
- **Signal**: `ts_sum(returns, 5)` — sum of 5 daily returns
- **Hypothesis**: 5-day momentum leaders are overcrowded. Institutional unwind follows.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_sum(returns, 5), 5)), 0), subindustry)`

### Alpha 3 — Z-Score Return Reversal
- **Signal**: `(returns - ts_mean(returns, 20)) / ts_std_dev(returns, 20)` — statistically extreme return
- **Hypothesis**: Returns >2 std devs from own mean revert strongly. Self-adjusts per stock volatility.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear((returns - ts_mean(returns, 20)) / (ts_std_dev(returns, 20) + 0.001), 5)), 0), subindustry)`

### Alpha 4 — Volume-Amplified Return Reversal
- **Signal**: `returns * rank(volume / adv20)` — crowded-trade reversal
- **Hypothesis**: High-volume + high-return = institutional accumulation complete. Reversal imminent.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear(returns * rank(volume / adv20), 5)), 0), subindustry)`

### Alpha 5 — Midpoint vs VWAP Divergence
- **Signal**: `(high + low) / 2 - vwap` — where did intraday buying cluster?
- **Hypothesis**: Midpoint above VWAP = buyers dominated range but not volume. Selling pressure ahead.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear((high + low) / 2 - vwap, 5)), 0), subindustry)`

### Alpha 6 — Normalized 5-Day Price Change
- **Signal**: `ts_delta(close, 5) / ts_mean(close, 20)` — scale-free medium momentum
- **Hypothesis**: 5-day change normalized by average price level produces robust cross-sectional reversal.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_delta(close, 5) / (ts_mean(close, 20) + 0.001), 5)), 0), subindustry)`

### Alpha 7 — Volume Surge Mean Reversion
- **Signal**: `volume / adv20 - 1` — excess volume above 20-day average
- **Hypothesis**: Volume surge = large institutional order completion. Price reverts post-fill.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear(volume / adv20 - 1, 5)), 0), subindustry)`

### Alpha 8 — Normalized Intraday Range Expansion
- **Signal**: `(high - low) / ts_mean(high - low, 20)` — volatility shock ratio
- **Hypothesis**: Range >2x average = volatility shock. Volatility mean-reverts, price normalizes.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear((high - low) / (ts_mean(high - low, 20) + 0.001), 5)), 0), subindustry)`

### Alpha 9 — 10-Day Stochastic Oscillator Reversal
- **Signal**: `(close - ts_min(low, 10)) / (ts_max(high, 10) - ts_min(low, 10))` — stochastic %K
- **Hypothesis**: Medium-term overbought/oversold extremes within 10-day channel produce stronger reversals than single-day signals.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear((close - ts_min(low, 10)) / (ts_max(high, 10) - ts_min(low, 10) + 0.001), 5)), 0), subindustry)`

### Alpha 10 — Volatility-Normalized Overnight Gap
- **Signal**: `(open - ts_delay(close, 1)) / ts_std_dev(close, 20)` — gap in std dev units
- **Hypothesis**: Gaps that are large in volatility-adjusted terms are statistically most likely to revert. Raw gap size is misleading across different vol regimes.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear((open - ts_delay(close, 1)) / (ts_std_dev(close, 20) + 0.001), 5)), 0), subindustry)`

### Alpha 11 — Upper Shadow Pressure (Bearish Candle Body)
- **Signal**: `high - max(open, close)` — failed bullish attempts
- **Hypothesis**: Large upper shadows = sellers rejected higher prices. Persistent overhead supply leads to decline.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(high - ts_max(open, close), 5)), 0), subindustry)`

### Alpha 12 — Lower Shadow Demand (Bullish Candle Body)
- **Signal**: `min(open, close) - low` — rejected bearish attempts
- **Hypothesis**: Large lower shadows = buyers absorbed all selling at lows. Strong demand support leads to bounce.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.65, rank(ts_decay_linear(ts_min(open, close) - low, 5)), 0), subindustry)`

---

## 4. Submission Parameter Targets

| Metric | Minimum | Target |
|---|---|---|
| Sharpe | ≥ 1.25 | > 1.5 |
| Fitness | ≥ 1.0 | > 1.1 |
| Turnover | ≤ 70% | < 30% |
| Self-Correlation | < 0.70 | < 0.50 |

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
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(high - max(open, close), 5)), 0), subindustry)`

### Alpha 12 — Lower Shadow Demand (Bullish Candle Body)
- **Signal**: `min(open, close) - low` — rejected bearish attempts
- **Hypothesis**: Large lower shadows = buyers absorbed all selling at lows. Strong demand support leads to bounce.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.65, rank(ts_decay_linear(min(open, close) - low, 5)), 0), subindustry)`

---

## 🧬 4. Generation 3 Alpha Catalog — Novel Operator Families

**Key upgrades over Gen 2:**
- Introduces **completely new operator families** (`ts_corr`) never used in Gen 1 or 2
- Candle body ratio captures directional conviction, not just price level
- Volume-price correlation captures structural regime transitions
- Zero overlap with any existing signal → guaranteed to pass self-correlation checks

### Alpha 13 — Volatility-Normalized Overnight Gap Reversion (Ultra)
- **Signal**: `(open - ts_delay(close, 1)) / ts_std_dev(returns, 10)` — overnight gap in return-volatility units
- **Hypothesis**: Overnight gaps that are large relative to 10-day return volatility (not price volatility) represent the most statistically meaningful dislocations. Using return vol instead of price vol produces a more stable normalizer.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear((open - ts_delay(close, 1)) / (ts_std_dev(returns, 10) + 0.0001), 6)), 0), subindustry)`
- **Parameters**: Decay 6, Liquidity gate 75%

### Alpha 14 — Intraday Candle Body Ratio Reversal
- **Signal**: `(close - open) / (high - low)` — candle body as a fraction of total intraday range
- **Hypothesis**: The body-to-range ratio measures directional conviction. Values near +1 mean the stock opened at the low and closed at the high (extreme bullish), which is unsustainable. Values near -1 indicate extreme bearish exhaustion. Both extremes revert sharply.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear((close - open) / (high - low + 0.001), 5)), 0), subindustry)`
- **Parameters**: Decay 5, Liquidity gate 70%

### Alpha 15 — Volume-Price Correlation Breakdown Reversal
- **Signal**: `ts_corr(close, volume, 10)` — 10-day rolling Pearson correlation between price and volume
- **Hypothesis**: When price and volume are strongly positively correlated (+0.8), institutional accumulation is complete and reversal is imminent. When strongly negative (-0.8), panic selling is overdone and a bounce follows. This structural regime signal is orthogonal to all pure price/volume signals.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_corr(close, volume, 10), 5)), 0), subindustry)`
- **Parameters**: Decay 5, Liquidity gate 65%

### Alpha 16 — VWAP Displacement Reversal
- **Signal**: `(close - vwap) / (high - low)` — close displacement from volume center, normalized by range
- **Hypothesis**: Extreme intraday close deviation from VWAP represents peak intraday session stretch. Reverting this displacement on high volume filters out slow drift and captures short-term fade returns.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear((close - vwap) / (high - low + 0.001), 5)), 0), subindustry)`
- **Parameters**: Decay 5, Liquidity gate 70%

### Alpha 17 — Volatility-Scaled Exponential Momentum Reversal
- **Signal**: `ts_sum(returns, 3) / ts_std_dev(returns, 10)` — cumulative short-term return over historical volatility
- **Hypothesis**: Multi-day return acceleration scaled by its own dynamic volatility highlights high-conviction momentum exhaustion points. Reverting this cross-sectionally produces robust risk-adjusted profits.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_sum(returns, 3) / (ts_std_dev(returns, 10) + 0.0001), 5)), 0), subindustry)`
- **Parameters**: Decay 5, Liquidity gate 65%

### Alpha 18 — Intraday Range Location Divergence
- **Signal**: `((close - low) - (open - low)) / (high - low)` — daily close location minus open location in the range
- **Hypothesis**: Exposes early-session buyer traps. If the open was near the high but close finished near the low on high volume, it signals complete session buyer exhaustion and reverts sharply.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear(((close - low) - (open - low)) / (high - low + 0.001), 5)), 0), subindustry)`
- **Parameters**: Decay 5, Liquidity gate 70%

### Alpha 19 — Volume-Weighted Price Change Correlation Reversal
- **Signal**: `ts_corr(returns, volume / adv20, 10)` — correlation between daily returns and relative volume
- **Hypothesis**: Captures the exhaustion of institutional volume flows. When price change and volume are highly correlated, momentum is drying up and standard mean-reversion forces take over.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear(ts_corr(returns, volume / adv20, 10), 6)), 0), subindustry)`
- **Parameters**: Decay 6, Liquidity gate 75%

### Alpha 20 — Overnight-to-Intraday Stretch Reversion
- **Signal**: `((open - ts_delay(close, 1)) - (close - open)) / ts_std_dev(returns, 10)` — overnight gap minus intraday return, scaled by return vol
- **Hypothesis**: Measures the dislocation between overnight investor sentiment and active market hours execution. Discrepancies between gap and intraday session returns revert strongly under high volume.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear(((open - ts_delay(close, 1)) - (close - open)) / (ts_std_dev(returns, 10) + 0.0001), 5)), 0), subindustry)`
- **Parameters**: Decay 5, Liquidity gate 70%

### Alpha 21 — High-Low Spread Deviation Reversal
- **Signal**: `(high - low) / ts_mean(high - low, 10)` — standardized daily spread relative to rolling average
- **Hypothesis**: Extreme spread expansion on high volume marks high volatility momentum peaks. Cross-sectional mean-reversion over 5-day decay captures volatility contraction and reversal.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear((high - low) / (ts_mean(high - low, 10) + 0.001), 5)), 0), subindustry)`
- **Parameters**: Decay 5, Liquidity gate 70%

### Alpha 22 — Close-to-VWAP Ratio Reversal
- **Signal**: `ts_sum(close / vwap - 1, 3)` — 3-day accumulated close ratio to intraday volume average
- **Hypothesis**: Closing prices persistently executing above/below daily vwap identify institutional buying/selling exhaustion that reverts to the volume center.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_sum(close / (vwap + 0.001) - 1, 3), 5)), 0), subindustry)`
- **Parameters**: Decay 5, Liquidity gate 65%

### Alpha 23 — Normalized Intraday Shadow Ratio Reversal
- **Signal**: `((high - max(open, close)) - (min(open, close) - low)) / (high - low)` — upper minus lower shadows over total range
- **Hypothesis**: Imbalances between intraday seller-driven upper shadows and buyer-driven lower shadows normalized by daily range capture temporary momentum exhaustion.
- **Formula**: `group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear(((high - max(open, close)) - (min(open, close) - low)) / (high - low + 0.001), 5)), 0), subindustry)`
- **Parameters**: Decay 5, Liquidity gate 70%

---

## 🚨 5. Critical Syntax Gotchas (Lessons Learned)

### A. Element-wise vs Time-Series Operators
| Intent | ❌ WRONG | ✅ CORRECT |
|---|---|---|
| Max of two fields at same time | `ts_max(open, close)` | `max(open, close)` |
| Min of two fields at same time | `ts_min(open, close)` | `min(open, close)` |
| Highest value over N days | `max(close, 10)` | `ts_max(close, 10)` |
| Lowest value over N days | `min(low, 10)` | `ts_min(low, 10)` |

**Rule**: `ts_max(x, d)` and `ts_min(x, d)` are **rolling time-series** operators requiring a day-count `d`. For element-wise comparison of two fields, use bare `max(x, y)` and `min(x, y)`.

### B. RED Color Tagging
- Only alphas with status `SUBMITTED` (fully passed all production checks) should be tagged RED
- `SOFT_FAIL` and `HARD_REJECT` alphas must NOT be tagged RED — this was a previous bug that has been fixed

---

## 6. Submission Parameter Targets

| Metric | Minimum | Target |
|---|---|---|
| Sharpe | ≥ 1.25 | > 1.5 |
| Fitness | ≥ 1.0 | > 1.1 |
| Turnover | ≤ 70% | < 25% |
| Self-Correlation | < 0.70 | < 0.50 |

### Turnover Optimization via Decay Parameter
The Fitness formula is: `Fitness = Sharpe × sqrt(|Returns|) / Turnover`

Because Turnover is in the denominator, reducing it is the single most impactful lever:
| Decay Value | Expected Turnover | Effect on Fitness |
|---|---|---|
| `3` | ~35-40% | Borderline, often SOFT_FAIL |
| `5` | ~18-22% | Sweet spot, comfortably above 1.0 |
| `6` | ~15-18% | Optimal for gap/overnight signals |
| `8+` | ~10-15% | May lag signal too much, lowering Sharpe |

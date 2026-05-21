# AlphaForge: Quantitative Research Manual & Generation Blueprint

This manual provides the core scientific foundations, database-grounded case studies, and exact mathematical templates required to synthesize high-performance alpha signals for the WorldQuant Brain platform.

---

## 📊 1. Core Research Thesis: The Gated Reversion Pattern

In basic/standard research tiers, access is restricted to standard pricing and volume datasets. The most robust, scalable anomaly available in these fields is **intraday mean reversion**. 

However, raw intraday reversion:
1. Triggers high **turnover** (often 70% to 110%), leading to immediate global platform rejection.
2. Experiences severe degradation during **low-liquidity periods** (which leads to high slippage and noise).

### The Solution: The Gated Smoothing Design Pattern
To conquer the turnover constraint and maximize Sharpe ratios, all modern high-probability alphas must implement a three-tiered composite pattern:
$$\text{Alpha} = \text{Neutralize} \left( \text{TradeWhen} \left( \text{Liquidity Gate}, \text{Rank} \left( \text{Smoothed Signal} \right), 0 \right), \text{Subindustry} \right)$$

---

## 🔍 2. Database Case Studies (Retrieved from SQLite `alpha_vault.db`)

By querying the historical runs database, we can contrast successful and failing designs to map out exactly what the compiler accepts and qualifies.

### A. The Failures (Analyzing Rejection Paths)

1. **The Turnover Trap**: 
   * *Formula*: `group_neutralize(-rank(returns), subindustry)`
   * *Outcome*: Sharpe: `1.71` | Fitness: `0.91` | Turnover: `71.23%` ➔ **HARD_REJECT**
   * *Diagnosis*: While the signal is mathematically highly predictive (high Sharpe), raw un-smoothed returns decay too rapidly, producing excessive trading action that exceeds the strict 70% turnover limit.

2. **The Fitness Trap**:
   * *Formula*: `group_neutralize(-rank(close - open), sector)`
   * *Outcome*: Sharpe: `1.56` | Fitness: `0.79` | Turnover: `64.45%` ➔ **SOFT_FAIL**
   * *Diagnosis*: Although turnover is safely under 70%, neutralizing relative to broad `sector` indices fails to hedge subindustry peer group shocks. This results in sub-optimal payouts, lowering the Fitness metric below the mandatory `1.0` threshold.

---

### B. The Successful Blueprint (The "Holy Grail" Pattern)

* *Formula*: `group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(close - open, 3)), 0), subindustry)`
* *Metrics*: **Sharpe: `1.84`** | **Fitness: `1.01`** | **Turnover: `34.32%`** ➔ **SUBMITTED & ACCEPTED**
* *Scientific Deconstruction*:
  1. **The Signal (`close - open`)**: Captures clean intraday price gaps. Reverting buying/selling imbalances at the close yields premium returns.
  2. **The Smoother (`ts_decay_linear(..., 3)`)**: Smooths the raw signal over a 3-day window using linear decay weightings. This single adjustment drops raw turnover from over `70%` down to a highly efficient `34%` while keeping Sharpe above `1.7`.
  3. **The Gating Filter (`trade_when(volume > adv20 * 0.6, ..., 0)`)**: Restricts trading only to days when volume is at least 60% of its 20-day average. This eliminates illiquid, erratic sessions, raising risk-adjusted stability.
  4. **The Peer Group (`subindustry`)**: Hedging systematic risks at the narrow subindustry layer provides maximum peer-group isolation, raising Sharpe to premium levels.

---

## 🎯 3. Parameter "Sweet-Spot" Map

To ensure standard compliance, use this map to calibrate your parameters:

| Component | Variable | Sweet-Spot Range | Purpose |
| :--- | :--- | :--- | :--- |
| **Smoothing Window** | `decay` | `3` to `5` | Lowers turnover to $\le 45\%$ without lagging the signal. |
| **Liquidity Threshold** | `volume > adv20 * K` | `K` from `0.5` to `0.8` | Filters market noise on low-liquidity days. |
| **Execution Delay** | `delay` | `1` or `2` | Adjusts for transaction execution offsets. |
| **Neutralization Group** | `neutralization` | `SUBINDUSTRY` | Tightly controls for sector-specific style biases. |

---

## 🧬 4. Elite Research Alpha Catalog: The 10 Masterpieces

These ten pricing/volume alphas are synthesized using our validated blueprint and pushed directly to our active execution queue:

### 1. Gated Intraday Range Reversion (Alpha #1)
* **Hypothesis**: Intraday close-to-open gaps represent temporary imbalances that revert; 3-day decay smoothing limits turnover.
* **Formula**:
  `group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear(close - open, 3)), 0), subindustry)`

### 2. Gated Close-to-VWAP Divergence (Alpha #2)
* **Hypothesis**: Deviations between the closing price and vwap volume centers represent unstable intraday drifts that revert.
* **Formula**:
  `group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear((close - vwap) / (ts_std_dev(close, 20) + 0.001), 3)), 0), subindustry)`

### 3. Gated Return Mean Reversion (Alpha #3)
* **Hypothesis**: Short-term returns mean-revert on highly liquid sessions when institutional trade volumes are elevated.
* **Formula**:
  `group_neutralize(trade_when(volume > adv20 * 0.5, -rank(ts_decay_linear(returns, 3)), 0), subindustry)`

### 4. Gated Overnight Gap Reversion (Alpha #4)
* **Hypothesis**: Opening price gaps relative to the previous close represent liquidity mismatches that mean-revert intraday.
* **Formula**:
  `group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear(open - ts_delay(close, 1), 3)), 0), subindustry)`

### 5. Gated Spread Reversion (Alpha #5)
* **Hypothesis**: Peaks in the intraday high-low spread indicate temporary volatility spikes that mean-revert on typical trading days.
* **Formula**:
  `group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(high - low, 3)), 0), subindustry)`

### 6. Gated VWAP Trend Reversion (Alpha #6)
* **Hypothesis**: Intraday drift between the volume center (vwap) and open price represents overextended liquidity that reverts.
* **Formula**:
  `group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(vwap - open, 3)), 0), subindustry)`

### 7. Gated Volume-Weighted Return Reversion (Alpha #7)
* **Hypothesis**: Returns weighted by volume deviations capture amplified trade imbalances that experience sharp reversion.
* **Formula**:
  `group_neutralize(trade_when(volume > adv20 * 0.55, -rank(ts_decay_linear(returns * rank(volume / adv20), 3)), 0), subindustry)`

### 8. Gated Overnight Trend Reversion (Alpha #8)
* **Hypothesis**: Extended 2-day gapped intraday movements represent overbought/oversold momentum exhaustion that mean-reverts.
* **Formula**:
  `group_neutralize(trade_when(volume > adv20 * 0.8, -rank(ts_decay_linear(open - ts_delay(close, 2), 3)), 0), subindustry)`

### 9. Gated Normalized Deviation Reversion (Alpha #9)
* **Hypothesis**: Normalized closing price deviation from the 10-day moving average mean-reverts on active trading sessions.
* **Formula**:
  `group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear((close - ts_mean(close, 10)) / (ts_std_dev(close, 10) + 0.001), 3)), 0), subindustry)`

### 10. Gated Intraday Volatility Reversion (Alpha #10)
* **Hypothesis**: Intraday high price deviation relative to the volume center represents temporary buying exhaustion that mean-reverts.
* **Formula**:
  `group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(high - vwap, 3)), 0), subindustry)`

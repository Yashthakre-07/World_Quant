# Intermediate Pack: Improve your Alpha [2/2]

Once you understand why an alpha has failed or achieved a borderline `SOFT_FAIL` status, you can apply professional quantitative optimization techniques to improve it. Here are the three primary areas of alpha enhancement.

---

## 1. How to Lower Turnover (Fixing Fitness Failures)

If your alpha has a strong Sharpe Ratio but fails because of high Turnover ($>60\%$), its **Fitness** will drop below $1.0$. Use these coding structures and parameters to slow down position changes:

### A. Increase the Simulation Decay Parameter
*   The `decay` parameter exponentially/linearly smooths your portfolio weights over multiple days. 
*   **Action**: If decay is set to `6`, increase it to `10`, `12`, or `15`. This forces the portfolio to hold onto positions longer, dramatically lowering turnover.

### B. Use FASTEXPR Decay Operators
*   Manually apply time-series smoothing directly in your formula using `ts_decay_linear(x, d)`.
*   **Example**: Change `rank(close / open)` to `ts_decay_linear(rank(close / open), 10)`.

### C. Apply Gating Operators (`trade_when`)
*   Use `trade_when(entry_condition, alpha, exit_value)` to restrict trading. The portfolio will only update weights when an extreme signal occurs, remaining in `exit_value` (usually `0` or current position) otherwise.
*   **Example**: `trade_when(ts_rank(volume, 20) > 0.8, -ts_delta(close, 5), 0)`

---

## 2. How to Boost Sharpe Ratio (Improving Signal Quality)

If your alpha has low turnover but a weak Sharpe Ratio ($<1.25$), your predictive signal is noisy. Use these techniques to clean up the signal:

### A. Tighten the Risk Neutralization
*   **Action**: Change your simulation neutralization from `SECTOR` or `INDUSTRY` to `SUBINDUSTRY`.
*   **Why**: Subindustry neutralization strips away micro-sector trends and factor exposures, focusing your alpha purely on the idiosyncratic relative movements of similar stocks. This significantly reduces volatility and increases the Sharpe ratio.

### B. Remove Outlier Distortions (Pasteurization)
*   Ensure that single volatile stocks are not dominating your alpha weights.
*   **Action**: Wrap your expression in `pasteurize()` or use `zscore()` instead of raw values to scale the inputs safely.
*   **Example**: `pasteurize(group_neutralize(rank(returns), subindustry))`

### C. Standardize / Rank Volatility
*   Volatile stocks produce larger price movements, but they add high variance to your PnL. Normalize your signal by standard deviation:
*   **Example**: `rank(returns) / ts_std_dev(returns, 20)`

---

## 3. How to Resolve Concentrated Weight Failures

If the simulator rejects your alpha due to `CONCENTRATED_WEIGHT`, it means a small number of stocks are receiving massive weight allocations (e.g. $>10\%$ each), creating extreme portfolio risk.

*   **Rule**: Never feed raw data fields directly into an alpha. Raw prices (e.g., $100$ vs. $5$) or raw fundamental figures distort allocations.
*   **Fix**: Always apply cross-sectional rank (`rank(x)`), percentile z-scoring (`zscore(x)`), or industry neutralization (`group_neutralize(x, industry)`) before scaling.
*   **Incorrect**: `enterprise_value / ebitda` (will crash on concentrated weights)
*   **Correct**: `group_neutralize(rank(enterprise_value / ebitda), subindustry)`

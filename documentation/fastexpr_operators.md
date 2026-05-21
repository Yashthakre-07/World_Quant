# FASTEXPR Operators Reference

WorldQuant FASTEXPR is a proprietary, matrix-based expression language optimized for high-performance financial time-series operations. It does not support standard control structures like `for` or `while` loops, instead operating cross-sectionally and along time dimensions using vectorized operations.

---

## 1. Cross-Sectional Normalization Operators
These operators evaluate values relative to all other instruments in the active universe at a single point in time.

*   `rank(x)`
    *   **Description**: Converts vector `x` into cross-sectional percentiles (values between `0.0` and `1.0`).
    *   **Usage**: `rank(close)`
    *   **Math**: $\text{rank}(x_i) = \frac{\text{Rank of } x_i \text{ in } x}{N}$ (where $N$ is the number of valid instruments).

*   `zscore(x)`
    *   **Description**: Standardizes cross-sectional values to have a mean of `0.0` and a standard deviation of `1.0`.
    *   **Usage**: `zscore(returns)`
    *   **Math**: $\text{zscore}(x_i) = \frac{x_i - \mu_{\text{cross}}}{\sigma_{\text{cross}}}$

*   `scale(x)`
    *   **Description**: Scales the absolute sum of the weights to equals `1.0`.
    *   **Usage**: `scale(returns)`
    *   **Math**: $x_i = \frac{x_i}{\sum |x_k|}$

*   `pasteurize(x)`
    *   **Description**: Truncates extreme outliers (winsorization) and scales weights safely to prevent extreme concentration. Recommended to resolve weight concentration failures.
    *   **Usage**: `pasteurize(group_neutralize(rank(returns), sector))`

---

## 2. Time-Series Operators
These operators compute historical metrics over a sliding time-series window of `d` business days.

*   `ts_delay(x, d)`
    *   **Description**: Returns the value of `x` from `d` business days ago.
    *   **Usage**: `ts_delay(close, 5)` (Close price 5 days ago).

*   `ts_delta(x, d)`
    *   **Description**: Computes the difference between the current value of `x` and its value `d` days ago.
    *   **Usage**: `ts_delta(close, 10)`
    *   **Math**: $x_t - x_{t-d}$

*   `ts_decay_linear(x, d)`
    *   **Description**: Computes a linearly weighted moving average over `d` days. Highly effective for smoothing signals and lowering turnover.
    *   **Usage**: `ts_decay_linear(returns, 10)`
    *   **Math**: Weighted average where weight of day $i$ (from current day $t$ down to $t-d+1$) decreases linearly: $w_i = d - i$.

*   `ts_mean(x, d)`
    *   **Description**: Simple arithmetic moving average over `d` days.
    *   **Usage**: `ts_mean(close, 20)`

*   `ts_std_dev(x, d)`
    *   **Description**: Standard deviation over `d` days.
    *   **Usage**: `ts_std_dev(returns, 20)`

*   `ts_sum(x, d)`
    *   **Description**: Sum of historical values over `d` days.
    *   **Usage**: `ts_sum(volume, 20)` (Total monthly volume).

*   `ts_rank(x, d)`
    *   **Description**: Returns the percentile rank of the current value of `x` relative to its own values over the last `d` days.
    *   **Usage**: `ts_rank(close, 20)`

*   `ts_max(x, d)` / `ts_min(x, d)`
    *   **Description**: Returns the highest or lowest value over a sliding `d` day window.
    *   **Usage**: `ts_max(high, 5)`

*   `ts_arg_max(x, d)` / `ts_arg_min(x, d)`
    *   **Description**: Returns the index (day number, from `0` to `d-1`) of the day where `x` achieved its maximum/minimum.
    *   **Usage**: `ts_arg_max(close, 10)`

*   `ts_corr(x, y, d)`
    *   **Description**: Rolling Pearson correlation between `x` and `y` over `d` days.
    *   **Usage**: `ts_corr(close, volume, 10)`

*   `ts_covariance(x, y, d)`
    *   **Description**: Rolling covariance between `x` and `y` over `d` days.
    *   **Usage**: `ts_covariance(returns, market_returns, 20)`

*   `ts_regression(y, x, d)`
    *   **Description**: Rolling linear regression slope of `y` on `x` over `d` days.
    *   **Usage**: `ts_regression(returns, volume, 10)`

---

## 3. Group and Neutralization Operators
These operators adjust variables against a cross-sectional grouping factor (e.g., Sector, Industry, or Subindustry) to strip away common market and industry risks.

*   `group_neutralize(x, group)`
    *   **Description**: Adjusts vector `x` so that the sum of the weights within each group equals `0.0` (zero-mean centering). This removes exposure to sector and industry beta.
    *   **Groups**: `sector`, `industry`, `subindustry`, or `market`.
    *   **Usage**: `group_neutralize(rank(returns), subindustry)`
    *   **Math**: $x_{i,\text{neutralized}} = x_i - \mu_{\text{group}(i)}$

*   `group_zscore(x, group)`
    *   **Description**: Standardizes vector `x` relative to other assets inside the same group.
    *   **Usage**: `group_zscore(returns, sector)`

*   `group_rank(x, group)`
    *   **Description**: Percentile ranks vector `x` relative only to other assets inside the same group.
    *   **Usage**: `group_rank(close, industry)`

---

## 4. Logical and Gating Operators
Used to create conditional exposures, segment strategies, or filter high-risk regimes.

*   `condition ? value_if_true : value_if_false`
    *   **Description**: Vectorized ternary conditional operator.
    *   **Usage**: `returns > 0 ? rank(volume) : -rank(volume)`

*   `trade_when(entry_condition, alpha_formula, exit_value)`
    *   **Description**: Gates transactions. Only takes or holds positions when the `entry_condition` is met (evaluates to true or `1`); otherwise drops back to the specified `exit_value` (commonly `0`). Highly effective for increasing Fitness and reducing whipsaw trading.
    *   **Usage**: `trade_when(abs(zscore(returns)) > 1.5, -rank(returns), 0)`

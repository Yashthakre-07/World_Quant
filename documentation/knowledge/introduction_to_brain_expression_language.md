# Introduction to BRAIN Expression Language (FastExpression)

The WorldQuant BRAIN platform uses a proprietary, matrix-based expression language called **FastExpression** (FASTEXPR). It is highly optimized for backtesting quantitative strategies across thousands of financial instruments over decades of historical data.

---

## 1. Core Language Design

FastExpression is designed to operate on two-dimensional arrays: **Time** (historical business days) and **Cross-section** (the asset universe). 

### Essential Language Characteristics:
*   **Vectorized Calculations**: All operators process complete arrays of data at once. You do not write explicit loops (no `for` or `while` statements).
*   **No Variable Declarations**: The language is strictly functional. You write expressions, not procedural scripts.
*   **Case-Sensitivity**: All operator names are strictly case-sensitive (e.g. `ts_mean` is valid, `TS_MEAN` is invalid).
*   **Implicit Parenthesization**: Expressions must be properly balanced. Complex operators can be nested within each other.

---

## 2. The Four Operator Families

FASTEXPR operators are categorized based on how they process the data matrix:

### A. Cross-Sectional Operators
These evaluate values relative to all other instruments in the active universe at a single point in time (column-wise).
*   `rank(x)`: Converts vector `x` into percentiles between `0.0` and `1.0`.
*   `zscore(x)`: Standardizes values to a mean of `0.0` and standard deviation of `1.0`.
*   `scale(x)`: Normalizes vector weights to sum to absolute `1.0`.

### B. Time-Series Operators
These process historical data along the time dimension for each stock individually (row-wise). They require a window parameter `d` (number of business days).
*   `ts_delay(x, d)`: Returns the value of `x` from `d` business days ago.
*   `ts_delta(x, d)`: Calculates $x_t - x_{t-d}$.
*   `ts_mean(x, d)`: Computes the rolling average of `x` over the past `d` days.
*   `ts_std_dev(x, d)`: Computes rolling standard deviation of `x`.
*   `ts_decay_linear(x, d)`: Returns a linearly-weighted moving average.

### C. Group and Neutralization Operators
These perform calculations relative to a cross-sectional grouping factor (like Sector, Industry, or Subindustry) to isolate specific stock characteristics.
*   `group_neutralize(x, group)`: Centered weights within each group to sum to zero.
*   `group_zscore(x, group)`: Standardizes `x` relative to its group.
*   `group_rank(x, group)`: Percentile ranks `x` within its group.

### D. Logical and Gating Operators
Used to construct conditional trading rules.
*   `condition ? value_if_true : value_if_false`: Vectorized ternary operator.
*   `trade_when(entry_condition, alpha_formula, exit_value)`: Restricts trades unless `entry_condition` evaluates to true.

---

## 3. Handling NaN and Infinite Values

In real financial data, missing values (NaNs) are common (e.g. suspended trading, delayed reports). 
*   **Default Behavior**: In FASTEXPR, operations involving NaNs generally propagate NaNs unless handled.
*   **Best Practices**:
    *   Set `"nanHandling": "OFF"` or rely on robust time-series smoothing to skip NaN slots.
    *   Avoid division by fields that can approach zero (like volume or small fundamental values) by adding a small constant offset (e.g., `volume + 0.0001`).
    *   Use `pasteurize()` to cap extreme values and manage outlier amplification.

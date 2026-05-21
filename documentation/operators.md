# WorldQuant Fast Expression Language (FEL) Operators Reference

This document serves as the absolute index of WorldQuant Formulaic Expression Language (FEL) operators.

---

## 1. Arithmetic & Mathematical Operators

Standard mathematical operators process input matrices element-by-element.

| Operator | Syntax | Description | Math |
| :--- | :--- | :--- | :--- |
| **Absolute** | `abs(x)` | Absolute value of $x$. | $|x_i|$ |
| **Logarithm** | `log(x)` | Natural logarithm of $x$. | $\ln(x_i)$ |
| **Sign** | `sign(x)` | Returns `-1` if $x < 0$, `0` if $x = 0$, and `1` if $x > 0$. | $\text{sgn}(x_i)$ |
| **Square Root** | `sqrt(x)` | Square root of $x$. | $\sqrt{x_i}$ |
| **Power** | `power(x, y)` | Raises $x$ to the power of $y$. | $x_i^{y_i}$ |
| **Maximum** | `max(x, y)` | Element-wise maximum of $x$ and $y$. | $\max(x_i, y_i)$ |
| **Minimum** | `min(x, y)` | Element-wise minimum of $x$ and $y$. | $\min(x_i, y_i)$ |

---

## 2. Time-Series Operators (ts_*)

These operators analyze chronological values for individual stocks over a sliding window of `d` business days.

| Operator | Syntax | Description |
| :--- | :--- | :--- |
| **Delay** | `ts_delay(x, d)` | Value of $x$, $d$ days ago. |
| **Delta** | `ts_delta(x, d)` | Difference between current $x$ and $x$ from $d$ days ago ($x_t - x_{t-d}$). |
| **Mean** | `ts_mean(x, d)` | Simple moving average over $d$ days. |
| **Sum** | `ts_sum(x, d)` | Cumulative sum over $d$ days. |
| **Max** | `ts_max(x, d)` | Highest value achieved in the past $d$ days. |
| **Min** | `ts_min(x, d)` | Lowest value achieved in the past $d$ days. |
| **ArgMax** | `ts_arg_max(x, d)` | Days ago (0 to $d-1$) where $x$ reached its highest value. |
| **ArgMin** | `ts_arg_min(x, d)` | Days ago (0 to $d-1$) where $x$ reached its lowest value. |
| **Standard Deviation** | `ts_std_dev(x, d)` | Standard deviation over a sliding $d$ day window. |
| **Correlation** | `ts_corr(x, y, d)` | Pearson correlation coefficient between $x$ and $y$ over $d$ days. |
| **Covariance** | `ts_covariance(x, y, d)` | Historical covariance of $x$ and $y$ over $d$ days. |
| **Rank** | `ts_rank(x, d)` | Percentile rank of current $x$ relative to its own $d$-day history. |
| **Linear Decay** | `ts_decay_linear(x, d)` | Linearly weighted moving average over $d$ days. Reduces Turnover. |
| **Exponential Decay** | `ts_decay_exponential(x, d)` | Exponentially weighted moving average over $d$ days. |
| **Regression Slope** | `ts_regression(y, x, d)` | Slope coefficient ($\beta$) of linear regression of $y$ on $x$ over $d$ days. |
| **Entropy** | `ts_entropy(x, d)` | Measures the randomness/complexity of $x$'s path over $d$ days. |

---

## 3. Cross-Sectional Operators

These operators execute comparison and normalization across all assets in the active universe at a single slice in time.

| Operator | Syntax | Description |
| :--- | :--- | :--- |
| **Rank** | `rank(x)` | Percentile ranks all values cross-sectionally to $[0, 1]$. |
| **Z-Score** | `zscore(x)` | Cross-sectional standardization (zero mean, unit variance). |
| **Scale** | `scale(x)` | Adjusts weights so the absolute sum equals 1.0 ($\sum \|x_i\| = 1$). |
| **Pasteurize** | `pasteurize(x)` | Winsorizes outliers and scales weights to prevent risk concentration. |
| **Purify** | `purify(x)` | Removes common market signal residual alignments. |

---

## 4. Group & Risk-Neutralization Operators

Crucial for neutralizing sector, industry, or subindustry risk bias.

| Operator | Syntax | Description |
| :--- | :--- | :--- |
| **Neutralize** | `group_neutralize(x, group)` | Centers $x$ around $0.0$ per group: $x_{i} - \mu_{\text{group}(i)}$. |
| **Group Rank** | `group_rank(x, group)` | Performs percentile ranking exclusively within each group. |
| **Group Z-Score** | `group_zscore(x, group)` | Performs Z-score standardization exclusively within each group. |

*Allowed Groups*: `market`, `sector`, `industry`, `subindustry`.

---

## 5. Logical & Conditional Operators

| Operator | Syntax | Description |
| :--- | :--- | :--- |
| **Ternary Operator** | `cond ? val_if_true : val_if_false` | Vectorized if-else logic. |
| **Trade Gating** | `trade_when(cond, alpha, exit)` | Executes `alpha` if `cond` is met; otherwise yields `exit` (e.g. 0). |
| **Comparison** | `>`, `<`, `>=`, `<=`, `==`, `!=` | Relational operations returning `1` for true and `0` for false. |
| **NaN Check** | `is_nan(x)` | Evaluates to `1` if element is missing/invalid, `0` otherwise. |

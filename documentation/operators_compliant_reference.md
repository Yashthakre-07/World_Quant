# WQ FEL Operators & Expressions Master Reference

This document serves as the unified index of FEL operators and event-timeline-compliant mathematical expressions for WorldQuant consensus/fundamental datasets.

---

## 1. Allowed & Whitelisted FEL Operators

| Operator Category | Operator Syntax | Description | Event Field Compatible? |
| :--- | :--- | :--- | :--- |
| **Cross-Sectional** | `rank(x)` | Maps values to percentile scores $[0.0, 1.0]$. | **Yes** (Primary Normalizer) |
| **Cross-Sectional** | `zscore(x)` | Cross-sectional standardization (mean 0, std 1). | **Yes** |
| **Cross-Sectional** | `scale(x)` | Standardizes weights to sum to 1.0. | **Yes** |
| **Cross-Sectional** | `pasteurize(x)` | Winsorizes outliers and scales weights. | **Yes** |
| **Group / Neutralize**| `group_neutralize(x, g)` | Centers values per group (e.g. `subindustry`). | **Yes** |
| **Group / Neutralize**| `group_zscore(x, g)` | Performs Z-score standardization within group. | **Yes** |
| **Group / Neutralize**| `group_rank(x, g)` | Performs percentile ranking within group. | **Yes** |
| **Logical / Gating** | `trade_when(cond, alpha, exit)` | Gates positions based on liquidity/volume hurdles. | **Yes** |
| **Logical / Gating** | `cond ? val_t : val_f` | Ternary conditional operator. | **Yes** |
| **Time-Series** | `ts_delay(x, d)` | Value of $x$ from $d$ days ago. | **No** (Must wrap in `rank()` first!) |
| **Time-Series** | `ts_delta(x, d)` | Difference $x_t - x_{t-d}$. | **No** (Must wrap in `rank()` first!) |
| **Time-Series** | `ts_rank(x, d)` | Rolling time-series percentile rank. | **No** (Must wrap in `rank()` first!) |
| **Time-Series** | `ts_decay_linear(x, d)` | Linearly decayed smoothing filter (for turnover). | **No** (Must wrap in `rank()` first!) |
| **Time-Series** | `ts_corr(x, y, d)` | Pearson correlation coefficient over time. | **No** (Must wrap in `rank()` first!) |
| **Arithmetic** | `divide(x, y)` / `x / y` | Element-wise division. | **No** (Cannot divide event by daily!) |
| **Arithmetic** | `abs(x)` | Absolute value. | **No** (Strictly blocked on event fields!) |

---

## 2. Event Timeline Compliance Cheat Sheet

Analyst consensus variables are sparse **Event Inputs**. Market metrics (price, volume, cap) are dense **Daily Inputs**. Because of this mismatch, follow these direct blueprints:

*   **Banned Division**: `anl_field / close` ❌
*   **Banned Smoothing**: `ts_decay_linear(anl_field, 5)` ❌
*   **Banned Time-Series**: `ts_delta(anl_field, 10)` ❌
*   **Banned Absolute Value**: `abs(anl_field)` ❌
*   **Banned Denominator Scalar**: `anl_field_A / (anl_field_B + 0.001)` ❌ (scalar addition `+` is blocked on event fields)

### 🟢 Compliant Matrix Solutions:
1.  **Time-Series Wrap**: Wrap the event field in `rank(...)` first:
    *   `ts_delta(rank(anl_field), 10)` (Valid ✅)
    *   `ts_decay_linear(rank(anl_field), 5)` (Valid ✅)
2.  **Cross-Sectional Scale-Normalization**: Use `rank(...)` or `group_neutralize(...)` to adjust for size instead of dividing by market cap:
    *   `group_neutralize(rank(anl_field), subindustry)` (Valid ✅)
3.  **Event-by-Event Ratio (No Offset Addition)**:
    *   `anl_field_A / anl_field_B` (Valid ✅)
4.  **Signal-Conditioned Return Correlation**:
    *   `ts_corr(returns, rank(anl_field), 10)` (Valid ✅)

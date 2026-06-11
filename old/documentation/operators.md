# WorldQuant Brain: Master Operators & Alpha Expressions Reference

> [!NOTE]
> This is a unified reference manual mapping all whitelisted mathematical and time-series operators from the **WorldQuant Brain / ACE API** alongside robust, compiler-compliant expressions for sparse fundamental/analyst datasets.

---

## 📂 Table of Contents
1. [Whitelisted FastExpr Operators (Direct from API)](#1-whitelisted-fastexpr-operators-direct-from-api)
2. [Event Timeline Safety Rules (Crucial for Consensus Datasets)](#2-event-timeline-safety-rules-crucial-for-consensus-datasets)
3. [Exhaustive Library of Non-Correlating Alpha Expressions](#3-exhaustive-library-of-non-correlating-alpha-expressions)

---

## 1. Whitelisted FastExpr Operators (Direct from API)

### Arithmetic Operators
| Operator | Definition | Description | Event Compatible? |
| :--- | :--- | :--- | :--- |
| `add(x, y)` or `x + y` | Sums elements wise. | `filter=true` treats NaNs as 0. | **Yes** (if both are events or both daily) |
| `subtract(x, y)` or `x - y` | Subtracts elements wise. | `filter=true` treats NaNs as 0. | **Yes** (if both are events or both daily) |
| `multiply(x, y)` or `x * y` | Multiplies elements. | `filter=true` treats NaNs as 0. | **Yes** (if both are events or both daily) |
| `divide(x, y)` or `x / y` | Division. | Division-by-zero is handled. | **No** (Cannot divide event by daily directly) |
| `abs(x)` | Absolute value. | Removes negative sign. | **No** (Strictly blocked on event inputs) |
| `log(x)` | Natural logarithm. | Transforms positive data. | **Yes** (Daily/Dense fields only) |
| `sqrt(x)` | Square root. | Non-negative root. | **Yes** (Daily/Dense fields only) |
| `sign(x)` | Sign indicator (+1, -1, 0). | Preserves NaNs. | **Yes** |
| `power(x, y)` | `x ^ y` | Element-wise power. | **Yes** (Daily/Dense fields only) |
| `signed_power(x, y)` | `x` to power of `y`. | Preserves sign of `x`. | **Yes** (Daily/Dense fields only) |
| `inverse(x)` | `1 / x` | Inverts elements. | **No** (Blocked on event inputs) |
| `pasteurize(x)` | Outlier filter. | Sets to NaN if INF or out of universe. | **Yes** |

### Time-Series Operators (ts_*)
> [!WARNING]
> **Timeline Boundary Warning**: Time-series operations (`ts_mean`, `ts_delta`, etc.) cannot ingest sparse raw event fields directly. You must normalise the field first (e.g. `rank(event_field)`) before passing it to any of these operators.

| Operator | Syntax | Description |
| :--- | :--- | :--- |
| **ts_delay** | `ts_delay(x, d)` | Returns the value of `x` from `d` business days ago. |
| **ts_delta** | `ts_delta(x, d)` | Difference between current value and value from `d` days ago (x_t - x_t-d). |
| **ts_mean** | `ts_mean(x, d)` | Simple moving average over `d` days. |
| **ts_sum** | `ts_sum(x, d)` | Sums values of `x` over the past `d` days. |
| **ts_std_dev** | `ts_std_dev(x, d)` | Rolling standard deviation (volatility) over `d` days. |
| **ts_corr** | `ts_corr(x, y, d)` | Pearson correlation coefficient between `x` and `y` over `d` days. |
| **ts_covariance** | `ts_covariance(y, x, d)` | Covariance between `y` and `x` over `d` days. |
| **ts_rank** | `ts_rank(x, d)` | Ranks current value of `x` relative to its own `d`-day history. |
| **ts_decay_linear** | `ts_decay_linear(x, d)` | Linearly weighted moving average. Reduces turnover. |
| **ts_zscore** | `ts_zscore(x, d)` | Standardizes values relative to their rolling historical average. |
| **ts_arg_max** | `ts_arg_max(x, d)` | Days since the maximum value occurred in the last `d` days. |
| **ts_arg_min** | `ts_arg_min(x, d)` | Days since the minimum value occurred in the last `d` days. |
| **ts_backfill** | `ts_backfill(x, d)` | Forward-fills NaNs with the most recent valid value from lookback `d`. |
| **days_from_last_change**| `days_from_last_change(x)`| Counts days since the value of `x` last changed. |
| **last_diff_value** | `last_diff_value(x, d)` | Most recent value different from current value in the last `d` days. |

### Cross-Sectional Operators
| Operator | Syntax | Description |
| :--- | :--- | :--- |
| **rank** | `rank(x)` | Percentile ranks all values cross-sectionally to [0.0, 1.0]. |
| **zscore** | `zscore(x)` | Cross-sectional standardization (mean = 0, std = 1). |
| **scale** | `scale(x)` | Scales weights so absolute sum equals 1.0. |
| **normalize** | `normalize(x)` | Centers daily cross-section by subtracting the market mean. |
| **quantile** | `quantile(x)` | Reshapes weights using standard statistical distributions. |
| **winsorize** | `winsorize(x, std=4)`| Limits extreme outliers to standard deviation thresholds. |

### Group & Risk-Neutralization Operators
| Operator | Syntax | Description |
| :--- | :--- | :--- |
| **group_neutralize** | `group_neutralize(x, group)` | Centers values to zero mean within group (e.g. `subindustry`). |
| **group_rank** | `group_rank(x, group)` | Ranks values relative only to other assets in the same group. |
| **group_zscore** | `group_zscore(x, group)` | Standardizes values relative only to assets in the same group. |
| **group_scale** | `group_scale(x, group)` | Normalizes values within each group to a range between 0 and 1. |
| **group_mean** | `group_mean(x, weight, group)`| harmonic mean of a field within each specified group. |

*Allowed Groups*: `market`, `sector`, `industry`, `subindustry`.

### Logical & Gating Operators
| Operator | Syntax | Description |
| :--- | :--- | :--- |
| **Ternary Operator** | `cond ? val_t : val_f` | Vectorized conditional logic. |
| **trade_when** | `trade_when(cond, alpha, exit)` | Activates `alpha` when `cond == 1`, else returns `exit`. |
| **is_nan** | `is_nan(x)` | Returns `1` if element is NaN, `0` otherwise. |

---

## 2. Event Timeline Safety Rules (Crucial for Consensus Datasets)

1.  **NO Raw Event Division by Daily Variables**:
    *   ❌ Banned: `anl14_eps_estimate / close` (Failed: `Operator divide does not support event inputs`)
    *   🟢 Compliant: Divide by another event field in the same domain, or use rank normalisation:
        *   `anl14_eps_estimate / (anl14_sales_estimate + 0.001)`
        *   `group_neutralize(rank(anl14_eps_estimate), subindustry)`
2.  **NO Raw Event Time-Series Smoothing**:
    *   ❌ Banned: `ts_decay_linear(anl14_eps_estimate, 10)` (Failed: `Operator ts_decay_linear does not support event inputs`)
    *   🟢 Compliant: Rank the event field first (if it's a daily count consensus) to map it to a daily timeline coordinate:
        *   `ts_decay_linear(rank(anl10_daily_count_field), 10)`
3.  **NO absolute values (abs) on raw event fields**:
    *   ❌ Banned: `abs(anl14_eps_estimate)` (Failed: `Operator abs does not support event inputs`)
    *   🟢 Compliant: Wrap the event field in rank first (if compatible daily consensus):
        *   `abs(rank(anl10_daily_count_field))`
4.  **NO Cross-Sectional Ranking on Raw Sparse Events**:
    *   ❌ Banned: `rank(anl14_eps_estimate)` (Failed: `Operator rank does not support event inputs`)
    *   🟢 Compliant: Rank is allowed ONLY on daily count consensus (like `analyst10` fields). Raw sparse forecasts (like `eps_estimate` or `sales_estimate` in `analyst14/15`) are blocked from cross-sectional ranking. Use `group_zscore` or neutralization settings to normalize size instead of raw `rank()`.
5.  **NO Constant Scalar Additions on Raw Sparse Events**:
    *   ❌ Banned: `anl14_sales_estimate + 0.001` (Failed: `Operator add does not support event inputs`)
    *   🟢 Compliant: Omit safety offsets entirely since WorldQuant has built-in division-by-zero protection that returns `NaN` safely. E.g. `anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / anl4_fs_basic_splt_v4_nd_sales_estimate`.


---

## 3. Exhaustive Library of Non-Correlating Alpha Expressions

Below is a curated set of **52 mathematically-diverse formulas** representing various orthogonal signals (Momentum, Mean Reversion, Group Z-Scores, Ternary Regimes, Ratios, and Multi-period lead-lags).

### Signal #01: Pearson correlation between daily returns and 1-day lagged consensus rank for anl4_fs_basic_splt_v4_nd_eps_estimate
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, ts_corr(returns, rank(anl4_fs_basic_splt_v4_nd_eps_estimate), 10), 0), subindustry)
```

### Signal #02: Pearson correlation between daily returns and 1-day lagged consensus rank for anl4_fs_basic_splt_v4_nd_sales_estimate
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, ts_corr(returns, rank(anl4_fs_basic_splt_v4_nd_sales_estimate), 12), 0), subindustry)
```

### Signal #03: Pearson correlation between daily returns and 1-day lagged consensus rank for anl4_fs_basic_splt_v4_nd_div_estimate
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, ts_corr(returns, rank(anl4_fs_basic_splt_v4_nd_div_estimate), 14), 0), subindustry)
```

### Signal #04: Pearson correlation between daily returns and 1-day lagged consensus rank for anl4_fs_detail_lt_v4_nd_estimate
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, ts_corr(returns, rank(anl4_fs_detail_lt_v4_nd_estimate), 16), 0), subindustry)
```

### Signal #05: Pearson correlation between daily returns and 1-day lagged consensus rank for anl4_fs_detail_estimates_advanced_af_nd_ebit_high
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, ts_corr(returns, rank(anl4_fs_detail_estimates_advanced_af_nd_ebit_high), 18), 0), subindustry)
```

### Signal #06: Pearson correlation between daily returns and 1-day lagged consensus rank for anl4_fs_detail_estimates_advanced_af_nd_ebit_low
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, ts_corr(returns, rank(anl4_fs_detail_estimates_advanced_af_nd_ebit_low), 20), 0), subindustry)
```

### Signal #07: Linearly decayed rank momentum delta over 5 days for anl10_salsmun_1qf_1008
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_decay_linear(rank(anl10_salsmun_1qf_1008) - ts_delay(rank(anl10_salsmun_1qf_1008), 5), 8), 0), subindustry)
```

### Signal #08: Linearly decayed rank momentum delta over 10 days for anl10_salsmun_2qf_1001
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_decay_linear(rank(anl10_salsmun_2qf_1001) - ts_delay(rank(anl10_salsmun_2qf_1001), 10), 10), 0), subindustry)
```

### Signal #09: Linearly decayed rank momentum delta over 5 days for anl10_salsmun_1yf_980
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_decay_linear(rank(anl10_salsmun_1yf_980) - ts_delay(rank(anl10_salsmun_1yf_980), 5), 12), 0), subindustry)
```

### Signal #10: Linearly decayed rank momentum delta over 10 days for anl10_netsmun_1qf_1056
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_decay_linear(rank(anl10_netsmun_1qf_1056) - ts_delay(rank(anl10_netsmun_1qf_1056), 10), 8), 0), subindustry)
```

### Signal #11: Linearly decayed rank momentum delta over 5 days for anl10_netsmun_2qf_1059
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_decay_linear(rank(anl10_netsmun_2qf_1059) - ts_delay(rank(anl10_netsmun_2qf_1059), 5), 10), 0), subindustry)
```

### Signal #12: Linearly decayed rank momentum delta over 10 days for anl10_netsmun_1yf_1051
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_decay_linear(rank(anl10_netsmun_1yf_1051) - ts_delay(rank(anl10_netsmun_1yf_1051), 10), 12), 0), subindustry)
```

### Signal #13: Time-series z-score of consensus rank for anl4_fs_detail_estimates_advanced_af_nd_ebit_high over 12 days
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, ts_zscore(rank(anl4_fs_detail_estimates_advanced_af_nd_ebit_high), 12), 0), subindustry)
```

### Signal #14: Time-series z-score of consensus rank for anl4_fs_detail_estimates_advanced_af_nd_ebit_low over 15 days
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, ts_zscore(rank(anl4_fs_detail_estimates_advanced_af_nd_ebit_low), 15), 0), subindustry)
```

### Signal #15: Time-series z-score of consensus rank for anl4_fs_detail_estimates_advanced_af_nd_fcf_high over 18 days
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, ts_zscore(rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high), 18), 0), subindustry)
```

### Signal #16: Time-series z-score of consensus rank for anl4_fs_detail_estimates_advanced_af_nd_fcf_low over 21 days
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, ts_zscore(rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_low), 21), 0), subindustry)
```

### Signal #17: Time-series z-score of consensus rank for anl4_fs_detail_estimates_advanced_af_nd_grossincome_high over 24 days
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, ts_zscore(rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_high), 24), 0), subindustry)
```

### Signal #18: Rolling time-series rank of anl10_fcfsmun_1qf_1989 over 15 days
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.65, ts_rank(rank(anl10_fcfsmun_1qf_1989), 15), 0), subindustry)
```

### Signal #19: Rolling time-series rank of anl10_fcfsmun_2qf_1956 over 17 days
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.65, ts_rank(rank(anl10_fcfsmun_2qf_1956), 17), 0), subindustry)
```

### Signal #20: Rolling time-series rank of anl10_fcfsmun_1yf_1986 over 19 days
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.65, ts_rank(rank(anl10_fcfsmun_1yf_1986), 19), 0), subindustry)
```

### Signal #21: Rolling time-series rank of anl10_ebismun_1qf_2214 over 21 days
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.65, ts_rank(rank(anl10_ebismun_1qf_2214), 21), 0), subindustry)
```

### Signal #22: Rolling time-series rank of anl10_ebismun_2qf_2231 over 23 days
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.65, ts_rank(rank(anl10_ebismun_2qf_2231), 23), 0), subindustry)
```

### Signal #23: Rolling time-series rank of anl10_ebismun_1yf_2212 over 25 days
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.65, ts_rank(rank(anl10_ebismun_1yf_2212), 25), 0), subindustry)
```

### Signal #24: Cross-sectional group-zscore of estimate rank for anl4_fs_basic_splt_v4_nd_eps_estimate normalized by subindustry
```fastexpr
trade_when(volume > adv20 * 0.80, group_zscore(rank(anl4_fs_basic_splt_v4_nd_eps_estimate), subindustry), 0)
```

### Signal #25: Cross-sectional group-zscore of estimate rank for anl4_fs_basic_splt_v4_nd_sales_estimate normalized by subindustry
```fastexpr
trade_when(volume > adv20 * 0.80, group_zscore(rank(anl4_fs_basic_splt_v4_nd_sales_estimate), subindustry), 0)
```

### Signal #26: Cross-sectional group-zscore of estimate rank for anl4_fs_basic_splt_v4_nd_div_estimate normalized by subindustry
```fastexpr
trade_when(volume > adv20 * 0.80, group_zscore(rank(anl4_fs_basic_splt_v4_nd_div_estimate), subindustry), 0)
```

### Signal #27: Cross-sectional group-zscore of estimate rank for anl4_fs_detail_lt_v4_nd_estimate normalized by subindustry
```fastexpr
trade_when(volume > adv20 * 0.80, group_zscore(rank(anl4_fs_detail_lt_v4_nd_estimate), subindustry), 0)
```

### Signal #28: Cross-sectional group-zscore of estimate rank for anl4_fs_detail_estimates_advanced_af_nd_ebit_high normalized by subindustry
```fastexpr
trade_when(volume > adv20 * 0.80, group_zscore(rank(anl4_fs_detail_estimates_advanced_af_nd_ebit_high), subindustry), 0)
```

### Signal #29: Difference of current rank of anl10_netsmun_2qf_1059 from its 10-day moving average
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_av_diff(rank(anl10_netsmun_2qf_1059), 10), 0), subindustry)
```

### Signal #30: Difference of current rank of anl10_netsmun_1yf_1051 from its 12-day moving average
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_av_diff(rank(anl10_netsmun_1yf_1051), 12), 0), subindustry)
```

### Signal #31: Difference of current rank of anl10_fcfsmun_1qf_1989 from its 14-day moving average
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_av_diff(rank(anl10_fcfsmun_1qf_1989), 14), 0), subindustry)
```

### Signal #32: Difference of current rank of anl10_fcfsmun_2qf_1956 from its 16-day moving average
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_av_diff(rank(anl10_fcfsmun_2qf_1956), 16), 0), subindustry)
```

### Signal #33: Difference of current rank of anl10_fcfsmun_1yf_1986 from its 18-day moving average
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_av_diff(rank(anl10_fcfsmun_1yf_1986), 18), 0), subindustry)
```

### Signal #34: Difference of current rank of anl10_ebismun_1qf_2214 from its 20-day moving average
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_av_diff(rank(anl10_ebismun_1qf_2214), 20), 0), subindustry)
```

### Signal #35: Ternary returns-based sign toggle for consensus rank of anl4_fs_basic_splt_v4_nd_div_estimate
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, returns < 0 ? -rank(anl4_fs_basic_splt_v4_nd_div_estimate) : rank(anl4_fs_basic_splt_v4_nd_div_estimate), 0), subindustry)
```

### Signal #36: Ternary returns-based sign toggle for consensus rank of anl4_fs_detail_lt_v4_nd_estimate
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, returns < 0 ? -rank(anl4_fs_detail_lt_v4_nd_estimate) : rank(anl4_fs_detail_lt_v4_nd_estimate), 0), subindustry)
```

### Signal #37: Ternary returns-based sign toggle for consensus rank of anl4_fs_detail_estimates_advanced_af_nd_ebit_high
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, returns < 0 ? -rank(anl4_fs_detail_estimates_advanced_af_nd_ebit_high) : rank(anl4_fs_detail_estimates_advanced_af_nd_ebit_high), 0), subindustry)
```

### Signal #38: Ternary returns-based sign toggle for consensus rank of anl4_fs_detail_estimates_advanced_af_nd_ebit_low
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, returns < 0 ? -rank(anl4_fs_detail_estimates_advanced_af_nd_ebit_low) : rank(anl4_fs_detail_estimates_advanced_af_nd_ebit_low), 0), subindustry)
```

### Signal #39: Ternary returns-based sign toggle for consensus rank of anl4_fs_detail_estimates_advanced_af_nd_fcf_high
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, returns < 0 ? -rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high) : rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high), 0), subindustry)
```

### Signal #40: Cross-sectional rank of Operating Margin ratio (anl4_fs_detail_estimates_advanced_af_nd_ebit_high / anl4_fs_basic_splt_v4_nd_sales_estimate)
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebit_high / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)
```

### Signal #41: Cross-sectional rank of Free Cash Margin ratio (anl4_fs_detail_estimates_advanced_af_nd_fcf_high / anl4_fs_basic_splt_v4_nd_sales_estimate)
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)
```

### Signal #42: Cross-sectional rank of Low-to-High EBIT Spread ratio (anl4_fs_detail_estimates_advanced_af_nd_ebit_low / anl4_fs_detail_estimates_advanced_af_nd_ebit_high)
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebit_low / anl4_fs_detail_estimates_advanced_af_nd_ebit_high), 0), subindustry)
```

### Signal #43: Cross-sectional rank of Low-to-High FCF Spread ratio (anl4_fs_detail_estimates_advanced_af_nd_fcf_low / anl4_fs_detail_estimates_advanced_af_nd_fcf_high)
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_low / anl4_fs_detail_estimates_advanced_af_nd_fcf_high), 0), subindustry)
```

### Signal #44: Cross-sectional rank of Gross Margin Consensus ratio (anl4_fs_detail_estimates_advanced_af_nd_grossincome_high / anl4_fs_basic_splt_v4_nd_sales_estimate)
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_high / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)
```

### Signal #45: Rolling covariance of returns with consensus estimate rank of anl4_fs_detail_estimates_advanced_af_nd_ebit_low
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_covariance(returns, rank(anl4_fs_detail_estimates_advanced_af_nd_ebit_low), 12), 0), subindustry)
```

### Signal #46: Rolling covariance of returns with consensus estimate rank of anl4_fs_detail_estimates_advanced_af_nd_fcf_high
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_covariance(returns, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high), 14), 0), subindustry)
```

### Signal #47: Rolling covariance of returns with consensus estimate rank of anl4_fs_detail_estimates_advanced_af_nd_fcf_low
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_covariance(returns, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_low), 16), 0), subindustry)
```

### Signal #48: Rolling covariance of returns with consensus estimate rank of anl4_fs_detail_estimates_advanced_af_nd_grossincome_high
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.75, ts_covariance(returns, rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_high), 18), 0), subindustry)
```

### Signal #49: Lead-lag momentum ratio (current rank over 5-day lagged rank) for anl10_salsmun_1qf_1008
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, rank(rank(anl10_salsmun_1qf_1008) / (ts_delay(rank(anl10_salsmun_1qf_1008), 5) + 0.001)), 0), subindustry)
```

### Signal #50: Lead-lag momentum ratio (current rank over 8-day lagged rank) for anl10_salsmun_2qf_1001
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, rank(rank(anl10_salsmun_2qf_1001) / (ts_delay(rank(anl10_salsmun_2qf_1001), 8) + 0.001)), 0), subindustry)
```

### Signal #51: Lead-lag momentum ratio (current rank over 11-day lagged rank) for anl10_salsmun_1yf_980
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, rank(rank(anl10_salsmun_1yf_980) / (ts_delay(rank(anl10_salsmun_1yf_980), 11) + 0.001)), 0), subindustry)
```

### Signal #52: Lead-lag momentum ratio (current rank over 14-day lagged rank) for anl10_netsmun_1qf_1056
```fastexpr
group_neutralize(trade_when(volume > adv20 * 0.70, rank(rank(anl10_netsmun_1qf_1056) / (ts_delay(rank(anl10_netsmun_1qf_1056), 14) + 0.001)), 0), subindustry)
```


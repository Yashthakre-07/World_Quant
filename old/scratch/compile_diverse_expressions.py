import sys
from pathlib import Path

# Paths
master_md_path = Path("c:/Users/Admin/Documents/VIBE_YT/wq/documentation/operators_and_expressions_master.md")
operators_md_path = Path("c:/Users/Admin/Documents/VIBE_YT/wq/documentation/operators.md")

# Fields we can use
ANALYST10_FIELDS = [
    "anl10_salsmun_1qf_1008", "anl10_salsmun_2qf_1001", "anl10_salsmun_1yf_980",
    "anl10_netsmun_1qf_1056", "anl10_netsmun_2qf_1059", "anl10_netsmun_1yf_1051",
    "anl10_fcfsmun_1qf_1989", "anl10_fcfsmun_2qf_1956", "anl10_fcfsmun_1yf_1986",
    "anl10_ebismun_1qf_2214", "anl10_ebismun_2qf_2231", "anl10_ebismun_1yf_2212"
]

ANALYST14_FIELDS = [
    "anl4_fs_basic_splt_v4_nd_eps_estimate", "anl4_fs_basic_splt_v4_nd_sales_estimate",
    "anl4_fs_basic_splt_v4_nd_div_estimate", "anl4_fs_detail_lt_v4_nd_estimate",
    "anl4_fs_detail_estimates_advanced_af_nd_ebit_high", "anl4_fs_detail_estimates_advanced_af_nd_ebit_low",
    "anl4_fs_detail_estimates_advanced_af_nd_fcf_high", "anl4_fs_detail_estimates_advanced_af_nd_fcf_low",
    "anl4_fs_detail_estimates_advanced_af_nd_grossincome_high", "anl4_fs_detail_estimates_advanced_af_nd_grossincome_low"
]

# We will construct 80+ expressions, ensuring completely different mathematical shapes (structures):
# Structure 1: ts_corr(returns, rank(field), lookback) -> Correlation
# Structure 2: ts_decay_linear(rank(field) - ts_delay(rank(field), d1), d2) -> Decay delta
# Structure 3: ts_zscore(rank(field), d) -> Time-Series Z-score
# Structure 4: ts_rank(rank(field), d) -> Time-Series rank
# Structure 5: group_zscore(rank(field), subindustry) -> Cross-sectional group z-score
# Structure 6: group_neutralize(ts_av_diff(rank(field), d), subindustry) -> Time-series mean deviation
# Structure 7: Ternary gate: (returns < 0) ? -rank(field) : rank(field)
# Structure 8: Multi-field ratio: rank(fieldA / fieldB)
# Structure 9: trade_when(vol_cond, rank(field), exit) -> Simple gated signal
# Structure 10: ts_decay_exponential or nested structures

expressions = []

# --- 1. Correlation Structures (ts_corr) ---
for idx, f in enumerate(ANALYST14_FIELDS[:6]):
    d = 10 + idx * 2
    expressions.append({
        "desc": f"Pearson correlation between daily returns and 1-day lagged consensus rank for {f}",
        "formula": f"group_neutralize(trade_when(volume > adv20 * 0.70, ts_corr(returns, rank({f}), {d}), 0), subindustry)"
    })

# --- 2. Decayed Momentum / Deltas (ts_decay_linear) ---
for idx, f in enumerate(ANALYST10_FIELDS[:6]):
    d_delta = 5 + (idx % 2) * 5
    d_decay = 8 + (idx % 3) * 2
    expressions.append({
        "desc": f"Linearly decayed rank momentum delta over {d_delta} days for {f}",
        "formula": f"group_neutralize(trade_when(volume > adv20 * 0.75, ts_decay_linear(rank({f}) - ts_delay(rank({f}), {d_delta}), {d_decay}), 0), subindustry)"
    })

# --- 3. Time-Series Z-Score (ts_zscore) ---
for idx, f in enumerate(ANALYST14_FIELDS[4:9]):
    d = 12 + idx * 3
    expressions.append({
        "desc": f"Time-series z-score of consensus rank for {f} over {d} days",
        "formula": f"group_neutralize(trade_when(volume > adv20 * 0.70, ts_zscore(rank({f}), {d}), 0), subindustry)"
    })

# --- 4. Time-Series Percentile Rank (ts_rank) ---
for idx, f in enumerate(ANALYST10_FIELDS[6:12]):
    d = 15 + idx * 2
    expressions.append({
        "desc": f"Rolling time-series rank of {f} over {d} days",
        "formula": f"group_neutralize(trade_when(volume > adv20 * 0.65, ts_rank(rank({f}), {d}), 0), subindustry)"
    })

# --- 5. Group Z-Score (group_zscore) ---
for idx, f in enumerate(ANALYST14_FIELDS[:5]):
    expressions.append({
        "desc": f"Cross-sectional group-zscore of estimate rank for {f} normalized by subindustry",
        "formula": f"trade_when(volume > adv20 * 0.80, group_zscore(rank({f}), subindustry), 0)"
    })

# --- 6. Time-Series Mean Deviation (ts_av_diff) ---
for idx, f in enumerate(ANALYST10_FIELDS[4:10]):
    d = 10 + idx * 2
    expressions.append({
        "desc": f"Difference of current rank of {f} from its {d}-day moving average",
        "formula": f"group_neutralize(trade_when(volume > adv20 * 0.75, ts_av_diff(rank({f}), {d}), 0), subindustry)"
    })

# --- 7. Ternary Directional Gating (Ternary Operator) ---
for idx, f in enumerate(ANALYST14_FIELDS[2:7]):
    expressions.append({
        "desc": f"Ternary returns-based sign toggle for consensus rank of {f}",
        "formula": f"group_neutralize(trade_when(volume > adv20 * 0.70, returns < 0 ? -rank({f}) : rank({f}), 0), subindustry)"
    })

# --- 8. Multi-Field Consensus Ratios (Size Normalization) ---
pairs = [
    ("anl4_fs_detail_estimates_advanced_af_nd_ebit_high", "anl4_fs_basic_splt_v4_nd_sales_estimate", "Operating Margin"),
    ("anl4_fs_detail_estimates_advanced_af_nd_fcf_high", "anl4_fs_basic_splt_v4_nd_sales_estimate", "Free Cash Margin"),
    ("anl4_fs_detail_estimates_advanced_af_nd_ebit_low", "anl4_fs_detail_estimates_advanced_af_nd_ebit_high", "Low-to-High EBIT Spread"),
    ("anl4_fs_detail_estimates_advanced_af_nd_fcf_low", "anl4_fs_detail_estimates_advanced_af_nd_fcf_high", "Low-to-High FCF Spread"),
    ("anl4_fs_detail_estimates_advanced_af_nd_grossincome_high", "anl4_fs_basic_splt_v4_nd_sales_estimate", "Gross Margin Consensus")
]
for idx, (f1, f2, name) in enumerate(pairs):
    expressions.append({
        "desc": f"Cross-sectional rank of {name} ratio ({f1} / {f2})",
        "formula": f"group_neutralize(trade_when(volume > adv20 * 0.75, rank({f1} / {f2}), 0), subindustry)"
    })

# --- 9. Rolling Covariance and Dispersion Correlation ---
for idx, f in enumerate(ANALYST14_FIELDS[5:9]):
    d = 12 + idx * 2
    expressions.append({
        "desc": f"Rolling covariance of returns with consensus estimate rank of {f}",
        "formula": f"group_neutralize(trade_when(volume > adv20 * 0.75, ts_covariance(returns, rank({f}), {d}), 0), subindustry)"
    })

# --- 10. Multi-Period Delay Leads and Lags ---
for idx, f in enumerate(ANALYST10_FIELDS[:4]):
    d = 5 + idx * 3
    expressions.append({
        "desc": f"Lead-lag momentum ratio (current rank over {d}-day lagged rank) for {f}",
        "formula": f"group_neutralize(trade_when(volume > adv20 * 0.70, rank(rank({f}) / (ts_delay(rank({f}), {d}) + 0.001)), 0), subindustry)"
    })

# Build the complete markdown content
md_content = """# WorldQuant Brain: Master Operators & Alpha Expressions Reference

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
    *   ❌ Banned: `anl14_eps_estimate / close`
    *   🟢 Compliant: Divide by another event field in the same domain, or use rank normalisation:
        *   `anl14_eps_estimate / (anl14_sales_estimate + 0.001)`
        *   `group_neutralize(rank(anl14_eps_estimate), subindustry)`
2.  **NO Raw Event Time-Series Smoothing**:
    *   ❌ Banned: `ts_decay_linear(anl14_eps_estimate, 10)`
    *   🟢 Compliant: Rank the event field first to map it to a daily timeline coordinate:
        *   `ts_decay_linear(rank(anl14_eps_estimate), 10)`
3.  **NO absolute values (abs) on raw event fields**:
    *   ❌ Banned: `abs(anl14_eps_estimate)`
    *   🟢 Compliant: Wrap the event field in rank first:
        *   `abs(rank(anl14_eps_estimate))`

---

## 3. Exhaustive Library of Non-Correlating Alpha Expressions

Below is a curated set of **""" + str(len(expressions)) + """ mathematically-diverse formulas** representing various orthogonal signals (Momentum, Mean Reversion, Group Z-Scores, Ternary Regimes, Ratios, and Multi-period lead-lags).

"""

for i, expr in enumerate(expressions):
    md_content += f"### Signal #{i+1:02d}: {expr['desc']}\n"
    md_content += f"```fastexpr\n{expr['formula']}\n```\n\n"

# Write out to both paths
with open(master_md_path, "w", encoding="utf-8") as f:
    f.write(md_content)

with open(operators_md_path, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"Successfully generated {len(expressions)} expressions and updated both documentation files.")

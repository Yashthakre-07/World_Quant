# WorldQuant Brain: Master Compiler Diagnostics & Syntax Correction Blueprint
**Target Datasets**: analyst4, analyst10, analyst14, analyst15, analyst16, analyst44, analyst45  
**Document Purpose**: Absolute reference directory of all compiled errors, platform restrictions, and exact mathematical corrections to ensure 100% first-pass compile rates.

---

## 📂 Diagnostic Index
1. [Event Timeline vs. Daily Matrix Mismatches (The Vector Collapse)](#1-event-timeline-vs-daily-matrix-mismatches-the-vector-collapse)
2. [Multi-Simulation Batch Rejections (Thundering Herd blocks)](#2-multi-simulation-batch-rejections-thundering-herd-blocks)
3. [Epsilon and Constant Math Restrictions on Event Inputs](#3-epsilon-and-constant-math-restrictions-on-event-inputs)
4. [Banned Time-Series and Cross-Sectional Event Operators](#4-banned-time-series-and-cross-sectional-event-operators)
5. [Verified Account-Level Variable Whitelists](#5-verified-account-level-variable-whitelists)
6. [FastExpr Syntax Gotchas & Argument Signatures](#6-fastexpr-syntax-gotchas--argument-signatures)
7. [Mathematical Edge Cases & Lookback Window Restrictions](#7-mathematical-edge-cases--lookback-window-restrictions)
8. [Logical Boolean Comparisons & Conditional Operators](#8-logical-boolean-comparisons--conditional-operators)
9. [Group Capitalization Constraints in Formula Strings](#9-group-capitalization-constraints-in-formula-strings)
10. [NaN Accumulation & Volatility Gate Protections](#10-nan-accumulation--volatility-gate-protections)

---

## 1. Event Timeline vs. Daily Matrix Mismatches (The Vector Collapse)

### The Error Signature
*   `Operator ts_delta does not support event inputs. (HARD_REJECT)`
*   `Operator rank does not support event inputs. (HARD_REJECT)`
*   `Operator trade_when does not support event inputs. (HARD_REJECT)`

### The Root Cause
The WorldQuant Brain platform stores price, volume, and returns as **MATRIX** fields (continuous, dense daily records with one float value per stock per day). Analyst consensus forecasts, target prices, and surprise metrics are **VECTOR** fields (sparse point-in-time event inputs). They only update on specific dates when analyst groups revise their expectations, leaving empty (NaN) cells on other days. Passing a raw sparse event vector directly to continuous daily operators like `ts_delta` or `rank` triggers a compiler failure because the lookback windows cannot calculate mathematical sequences over NaN gaps.

### ❌ Non-Compliant Pattern
```fastexpr
// CRASH: ts_delta and rank cannot handle sparse timelines directly
rank(ts_delta(anl4_fs_basic_splt_v4_nd_eps_estimate, 5))
```

### ✅ Compliant Corrections

#### Method A: Vector-Average Matrix Reduction (Aggregated Vectors)
Wrap the sparse vector field in `vec_avg(...)` to calculate the average of all active analyst elements for each day. This reduces the sparse vector to a continuous daily MATRIX timeline.
```fastexpr
// COMPLIANT: vec_avg reduction converts the vector to a daily matrix
rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 5))
```

#### Method B: Chronological Backfill Transition (Event Matrices)
For fundamental event fields that represent matrices rather than lists, apply `ts_backfill(x, 252)` to carry the last observed revision forward up to a full trading year, removing NaN gaps.
```fastexpr
// COMPLIANT: ts_backfill populates the gaps to form a dense daily matrix
ts_decay_linear(rank(ts_backfill(anl14_mean_eps_fp1, 252)), 10)
```

---

## 2. Multi-Simulation Batch Rejections (Thundering Herd Blocks)

### The Error Signature
*   `Child simulation failed on WQ cluster. (HARD_REJECT)`

### The Root Cause
To optimize backtesting speed and navigate the platform's 3-slot concurrency limit, our pipeline groups alphas into **batches of up to 10** sent via Multi-Simulation API payloads. The WorldQuant cluster compiles the entire batch as a single execution tree. If **even one single formula** inside that batch of 10 contains an invalid operator, a spelling error, or an un-whitelisted variable, the cluster compiler **rejects the entire batch**. This results in all 10 alphas in that batch showing `ERROR` status with the generic message `Child simulation failed on WQ cluster`.

### ❌ Non-Compliant Pattern
```json
[
  {"formula": "group_neutralize(trade_when(volume > adv20 * 0.7, rank(ts_delta(vec_avg(anl4_eps), 5)), 0), subindustry)"},
  {"formula": "group_neutralize(trade_when(volume > adv20 * 0.7, rank(ts_delta(vec_avg(anl44_num_buys), 5)), 0), subindustry)"} 
]
// CRASH: If 'anl44_num_buys' is not subscribed/whitelisted, BOTH of these alphas fail with "Child simulation failed".
```

### ✅ Compliant Correction
Every formula submitted in a batch must be pre-validated against the exact whitelist database before API construction. If a single field cannot be found in your active profile's `fields.json` whitelist, it must be discarded prior to batching.

---

## 3. Epsilon and Constant Math Restrictions on Event Inputs

### The Error Signature
*   `Operator add does not support event inputs. (HARD_REJECT)`
*   `Operator divide does not support event inputs. (HARD_REJECT)`

### The Root Cause
In standard pricing/volume alphas, researchers add small constants (e.g. `+ 0.001` or `+ 0.0001` to denominators) to prevent division-by-zero crashes. However, because analyst estimate variables are sparse event records, the compiler strictly prohibits standard arithmetic addition (`+`) or subtraction (`-`) between raw event inputs and scalar constants. Furthermore, you cannot divide a raw event variable by a daily scale variable (like price or `cap`) using the standard `/` operator because their timeline matrices do not align.

### ❌ Non-Compliant Pattern
```fastexpr
// CRASH: Cannot add scalar constant 0.001 to a sparse event input
anl4_fs_basic_splt_v4_nd_eps_estimate + 0.001

// CRASH: Cannot divide event estimate directly by daily market cap
anl4_fs_basic_splt_v4_nd_sales_estimate / (cap + 0.001)
```

### ✅ Compliant Corrections

#### Method A: Safe Event-by-Event Margin Normalization
You are permitted to divide an event variable by another event variable within the **same timeline domain** (e.g. EBITDA consensus divided by Sales consensus). Ensure no scalar offsets are added to the denominator; the compiler handles event-based division natively.
```fastexpr
// COMPLIANT: Event / Event division is permitted without offsets
anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / anl4_fs_basic_splt_v4_nd_sales_estimate
```

#### Method B: Scale-Free Percentile Ranks
Rely entirely on `rank()` and `group_neutralize()` wrappers on your vector-averaged matrices. Ranking maps all asset values to a scale-free percentile domain $[0.0, 1.0]$, stripping out size bias naturally without requiring any division.
```fastexpr
// COMPLIANT: Percentile ranking naturally normalizes scale across assets
group_neutralize(rank(vec_avg(anl4_fs_basic_splt_v4_nd_sales_estimate)), subindustry)
```

---

## 4. Banned Time-Series and Cross-Sectional Event Operators

### The Error Signature
*   `Operator ts_decay_linear does not support event inputs. (HARD_REJECT)`
*   `Operator ts_corr does not support event inputs. (HARD_REJECT)`
*   `Operator abs does not support event inputs. (HARD_REJECT)`

### The Root Cause
Rolling window transformations and mathematical operators require uninterrupted sequences of daily observations. Because raw event vectors are populated sporadically, the following operators are **strictly banned** from direct execution on raw event variables:

| Banned Event Operator | Why it Fails | Compliant Replacement |
|---|---|---|
| `ts_delta(event, N)` | Window cannot calculate changes over empty days | `ts_delta(vec_avg(event), N)` |
| `ts_decay_linear(event, N)` | Cannot smooth sparse event data | `ts_decay_linear(vec_avg(event), N)` |
| `ts_corr(returns, event, N)` | Requires dense matrix alignment | `ts_corr(returns, vec_avg(event), N)` |
| `abs(event)` | Blocked on raw event inputs | Remove `abs()` entirely; utilize `rank()` |
| `rank(event)` | Cannot rank sparse vector lists cross-sectionally | `rank(vec_avg(event))` |

---

## 5. Verified Account-Level Variable Whitelists

Referencing a variable that is not subscribed to or whitelisted on your active profile triggers an immediate compiler block. **Do not use any variable outside this verified list**:

### 📁 Dataset: analyst4 (Verified Fundamental Estimates)
*   `anl4_fs_basic_splt_v4_nd_eps_estimate` (EPS Consensus Estimate)
*   `anl4_fs_basic_splt_v4_nd_sales_estimate` (Sales Consensus Estimate)
*   `anl4_fs_detail_estimates_advanced_af_nd_ebitda_high` (EBITDA High Consensus)
*   `anl4_fs_detail_estimates_advanced_af_nd_ebitda_low` (EBITDA Low Consensus)
*   `anl4_fs_detail_estimates_advanced_af_nd_ebitda_mean` (EBITDA Mean Consensus)
*   `anl4_fs_detail_estimates_advanced_af_nd_ptp_high` (Pre-tax Profit High)
*   `anl4_fs_detail_estimates_advanced_af_nd_ptp_low` (Pre-tax Profit Low)
*   `anl4_fs_detail_estimates_advanced_af_nd_ptp_mean` (Pre-tax Profit Mean)
*   `anl4_fs_detail_estimates_advanced_af_nd_fcf_high` (Free Cash Flow High)
*   `anl4_fs_detail_estimates_advanced_af_nd_fcf_low` (Free Cash Flow Low)

### 📁 Dataset: analyst16 (Verified Real-Time Estimates)
*   `anl16_actsurprise` (Consensus Actual Earnings Surprise)
*   `anl16_actsuescore` (Standardized Unexpected Earnings Score)
*   `anl16_actgrowth` (Consensus Earnings Growth)
*   `anl16_actstability` (Consensus Earnings Stability)
*   `anl16_actvalue` (Consensus Earnings Value)
*   *Note: `anl16_sue` is un-subscribed and will fail.*

### 📁 Dataset: analyst44 (Verified Broker Recommendation)
*   `anl44_analyst` (Consensus Recommendation Score)
*   *Note: `anl44_num_buys`, `anl44_num_sells`, `anl44_num_holds`, and `anl44_target_price` are un-subscribed and will fail.*

### 📁 Dataset: analyst45 (Verified Trade Ideas)
*   `anl45_ad_rel_ret_per` (Analyst Relative Return Performance)
*   `anl45_jensensalpha` (Consensus Jensen's Alpha Metric)
*   `anl45_beta` (Consensus Beta Factor)
*   `anl45_ad_ret_per` (Analyst Absolute Return Performance)
*   *Note: `anl45_hit_rate` and `anl45_avg_ret` are un-subscribed and will fail.*

---

## 6. FastExpr Syntax Gotchas & Argument Signatures

Ensuring correct syntax formatting prevents parsing-level failures at the local dashboard validator:

### A. Element-Wise vs. Rolling Time-Series Bounds
*   `ts_max(x, d)` and `ts_min(x, d)` are **rolling time-series** operators requiring a lookback window `d`.
*   `max(x, y)` and `min(x, y)` are **element-wise** comparison operators requiring two fields or variables.
*   *Incorrect*: `ts_max(open, close)` or `max(close, 10)`
*   *Correct*: `max(open, close)` or `ts_max(close, 10)`

### B. Nested Wrapper Parameter Mapping
Operators like `group_neutralize(x, group)` take exactly two arguments. A common syntax error is wrapping the group argument inside the nested child functions.
*   *Incorrect*: `group_neutralize(rank(close - open, subindustry))`
*   *Correct*: `group_neutralize(rank(close - open), subindustry)`

### C. Logic Operators
*   Never write standard Python logical operators (`and`, `or`, `not`) inside FastExpr.
*   Always use verified logical operators (`&&`, `||`, `!`).

---

## 7. Mathematical Edge Cases & Lookback Window Restrictions

### Lookback Parameter Datatypes
*   Time-series window arguments ($d$) must strictly be **positive integers** greater than or equal to `2`. 
*   Passing non-integers, zeros, or negative values into operators like `ts_delay(x, 5.5)`, `ts_delta(x, 0)`, or `ts_corr(x, y, -5)` will trigger a validation rejection.
*   *Incorrect*: `ts_delta(close, 3.5)`
*   *Correct*: `ts_delta(close, 4)`

### Minimum Window Lengths
*   Certain statistical operators like `ts_std_dev(x, d)` and `ts_corr(x, y, d)` compute variance metrics requiring a minimum window length to avoid mathematical division-by-zero inside their internal loops. Avoid lookbacks smaller than `5` for variance metrics.
*   *Incorrect*: `ts_corr(returns, volume, 2)`
*   *Correct*: `ts_corr(returns, volume, 10)`

---

## 8. Logical Boolean Comparisons & Conditional Operators

### Naked Booleans
FastExpr is a strongly-typed mathematical engine. You cannot pass a raw boolean expression (like `close > open`) directly to arithmetic, time-series, or ranking operators. You must convert it to numerical format using the conditional ternary operator `? :`.
*   *Incorrect*: `group_neutralize(rank(close > open), subindustry)`
*   *Correct*: `group_neutralize(rank((close > open) ? 1.0 : -1.0), subindustry)`

### ternary Fallback Defaults
*   Ensure that the conditional fallback values match the numeric expected type. The syntax structure is strictly `(condition) ? value_if_true : value_if_false`.
*   *Correct*: `(returns < 0) ? -rank(volume) : rank(volume)`

---

## 9. Group Capitalization Constraints in Formula Strings

### Capitalization of Group Tokens
*   While simulation configuration dictionaries accept uppercase values for serialization settings (e.g. `"neutralization": "SUBINDUSTRY"`), formula strings parsed inside FastExpr expressions must strictly use **lowercase** for group identifiers.
*   Passing capitalized tokens like `SUBINDUSTRY` or `SECTOR` inside the formula text will cause a syntax parser crash.
*   *Incorrect*: `group_neutralize(rank(close), SUBINDUSTRY)`
*   *Correct*: `group_neutralize(rank(close), subindustry)`

---

## 10. NaN Accumulation & Volatility Gate Protections

### NaN Cascade
While the backtester is designed to bypass occasional `NaN` values, deep cascading formulas (like taking `ts_corr` of a highly volatile division quotient) can generate continuous sequences of NaNs on illiquid or newly-listed assets. If the final vector contains more than `80%` NaN elements across the active cross-section, the cluster will reject the alpha for low coverage.
*   *Mitigation*: Guard all denominators using `+ 0.001` or `+ 0.0001` safety buffers for MATRIX variables.

### Volatility / Volume Gate Standardization
A volume gate (`trade_when(volume > adv20 * VOL_GATE, ...)`) is mandatory for all submitted alphas to ensure liquidity.
*   If `adv20` drops to `0` (for halted stocks), the gate expression would crash. Guard the volume gate by ensuring `adv20` is positive or rely on WQ's standard volume gate multiplier syntax.
*   *Enforced Template*: `trade_when(volume > adv20 * 0.70, <formula>, 0)`

# Master Compile Error Report - WorldQuant Brain Diagnostics

This report compiles and analyzes the recent remote simulation failures on the WQ cluster to build a global blacklist and prevent future batch collapses.

---

## 📂 Master Failure Database & Blacklist

### 1. The Variable Whitelist Fallacy (Critical Unknown Identifier Collapse)
- **Error Signature**: `Child simulation failed on WQ cluster. (HARD_REJECT)`
- **Failed Fields**: `anl4_afv4_eps_mean`, `anl4_ebitda_mean`, `anl14_actvalue_eps_fp0`, `anl14_high_eps_fp1`, `anl14_high_ebitda_fp1`, `average_daily_relative_return_percent`, `relative_return_percent_today`.
- **Root Cause**: The active profile has a custom whitelist of variables. Attempting to use generic names (e.g. `anl4_afv4_eps_mean` instead of the whitelisted `anl4_fs_basic_splt_v4_nd_eps_estimate`) causes the WQ cluster compiler to reject the variable. Because WQ processes batches together, a single unknown variable collapses the entire simulation tree for the batch.
- **Global Blacklist Rule**:
  - **ONLY** use verified whitelisted variable IDs present in the `whitelisted_variables` table of the database.
  - **Compliant Mappings**:
    - Instead of `anl4_afv4_eps_mean` $\rightarrow$ use `anl4_fs_basic_splt_v4_nd_eps_estimate`.
    - Instead of `anl4_ebitda_mean` $\rightarrow$ use `anl4_fs_detail_estimates_advanced_af_nd_ebitda_mean`.
    - Instead of `anl14_actvalue_eps_fp0` or `anl14_high_eps_fp1` $\rightarrow$ use `anl14_mean_eps_fp1`.
    - Instead of `average_daily_relative_return_percent` or `relative_return_percent_today` $\rightarrow$ use `anl45_ad_rel_ret_per`.

### 2. The Vector Fallacy on Trade Ideas
- **Error Signature**: `Operator ts_delta does not support event inputs. (HARD_REJECT)`
- **Failed Fields**: `anl45_ad_rel_ret_per` (formerly referenced as `average_daily_relative_return_percent`).
- **Root Cause**: Trade ideas in `analyst45` represent analyst-level event recommendations. Under the compiler, these fields are stored as sparse **VECTOR** types, not daily matrices. Removing the `vec_avg(...)` aggregation wrapper triggers the event input compiler error when evaluated by continuous daily operators like `ts_delta` or arithmetic multipliers.
- **Global Blacklist Rule**:
  - **ALWAYS** wrap `anl45_ad_rel_ret_per`, `anl45_jensensalpha`, `anl45_beta`, and `anl45_ad_ret_per` in `vec_avg(...)` before applying mathematical operators (e.g. `vec_avg(anl45_ad_rel_ret_per)`).

---

## 🛠️ Corrective Formula Re-Engineering (100% Compiler-Safe)

To resolve the 20 compilation and simulation failures, we transitioned the portfolio to use the exact whitelisted variables and re-applied correct `vec_avg(...)` wrappers:

1. **Alpha 1**: `group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 10)), 0), subindustry)`
2. **Alpha 7**: `group_neutralize(trade_when(volume > adv20 * 0.67, rank(ts_delta(ts_backfill(anl14_mean_eps_fp1, 252), 22)), 0), subindustry)`
3. **Alpha 13**: `group_neutralize(trade_when(volume > adv20 * 0.65, rank(ts_delta(vec_avg(anl45_jensensalpha), 25)), 0), subindustry)`
4. **Alpha 15**: `group_neutralize(trade_when(volume > adv20 * 0.72, rank(ts_delta(vec_avg(anl45_ad_rel_ret_per), 15)), 0), subindustry)`
5. **Alpha 20 (Hybrid)**: `group_neutralize(trade_when(volume > adv20 * 0.66, rank(ts_delta(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ebitda_mean), 10) * vec_avg(anl45_ad_rel_ret_per)), 0), subindustry)`

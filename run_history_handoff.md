# RUN HISTORY & ACTIVE HANDOFF DOCUMENT

> [!IMPORTANT]
> If a model limit is hit, or you switch profiles/models/accounts, use this file to immediately pick up where the previous session left off. Do not try to guess or re-invent past state.

---

## 🎯 Current Context & Project Setup

1. **Active Region / Universe:** USA TOP3000 (D1 Delay)
2. **Current Goal:** Discover and evolve alphas using whitelisted fundamental/analyst datasets.
3. **Whitelisted Datasets & Fields:**
   - `analyst4` (Point-in-time Event variables):
     - `anl4_fs_basic_splt_v4_nd_eps_estimate`
     - `anl4_fs_basic_splt_v4_nd_sales_estimate`
     - `anl4_fs_detail_estimates_advanced_af_nd_ebitda_mean / high / low`
     - `anl4_fs_detail_estimates_advanced_af_nd_ptp_mean / high / low`
     - `anl4_fs_detail_estimates_advanced_af_nd_fcf_high / low`
   - `analyst14` (Dense matrix fundamental consensus):
     - `anl14_mean_eps_fp1`
     - `anl14_mean_revenue_fp1`
   - `analyst45` (Trade conviction metrics):
     - `anl45_jensensalpha`
     - `anl45_beta`
     - `anl45_ad_ret_per`
     - `anl45_ad_rel_ret_per`

---

## ⚡ Active State (As of June 3, 2026, 10:17 Local Time)

*   **Generation 4 (Current Evolving Batch):**
    *   **Queue Status:** Successfully generated and pushed **exactly 30 whitelisted analyst alphas** to `alpha_maker/generation_4_alphas.json`.
    *   **Execution:** Overwrote the remote active simulation queue via POST to `/api/overwrite-queue` (`overwritten_count: 30`).
    *   **Pipeline Daemon:** Successfully restarted the local tracking daemon `aql_unified_pipeline.py` after system restart.
    *   **Live Status:** Active backtests are running in the cloud. The pipeline daemon is polling them.



---

## 🔑 Hard Rules for the Incoming AI Agent (Must Follow)

1. **Vector-to-Matrix Rule:** All point-in-time event inputs (from `analyst4`) **must** be wrapped in `vec_avg(...)` before any mathematical, ranking, or time-series operations (e.g. `rank(vec_avg(field))`).
2. **No Event Constant Addition:** The WQ compiler rejects adding/subtracting scalar constants from raw events (e.g., `event + 0.001` or `event - 0.01` is strictly banned). Division by constants is also banned. Either divide by safe variables (`sales_estimate`), use rank spreads (`rank(A) - rank(B)`), or let the compiler handle zero division natively.
3. **Timeseries Backfilling:** Always use `ts_backfill(field, 252)` on dense matrix consensus inputs (like `anl14_mean_eps_fp1` or `anl45_jensensalpha`) to cover missing intervals in time-series operations (`ts_delta`, `ts_corr`, etc.).
4. **Group Neutralization Case:** Inside the formula, the neutralization must always be lowercase `subindustry`.
5. **Decay Setting:** Use high decay constants (`decay: 8` or `decay: 10`) for fundamental analyst metrics inside the payload config to prevent high turnover rejects.
6. **10-Minute Timeout Rule:** If an alpha stays in the `SIMULATING` state for over 10 minutes (600s), pull results anyway and mark it as failed/stuck. Do not let the pipeline hang.

---

## 🚀 Step-by-Step Next Actions

1. **Check Pipeline Status:**
   Run a GET request to `https://world-quant.onrender.com/api/queue-status` or read the local python log tail (`scratch/aql_run_log.txt`) to check if the 20 Generation 3 alphas have completed simulation.
2. **Analyze Results:**
   Once `queue_status` returns `pipeline_status == "COMPLETED"`, the daemon will automatically write the results to `alpha_maker/simulation_results_*.json`. Read this file to check:
   - Compile Success rates.
   - Highest Sharpe and Fitness.
   - Identify failures and reasons.
3. **Evolve Generation 4:**
   - Retrieve successful parent formulas.
   - Apply parameters/lookback shifts (e.g., changing `ts_delta(x, 10)` to `ts_delta(x, 15)` or `ts_delta(x, 8)`).
   - Write the evolved portfolio to `alpha_maker/generation_4_alphas.json`.
   - The daemon will detect the file and push the formulas to the remote review box.

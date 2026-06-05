# WorldQuant Brain: Master Expression & Formulaic Alpha Reference Guide

This document serves as the absolute global reference index of validated, working mathematical expressions and compiler-compliant syntax models for the WorldQuant Brain platform. It is designed to ensure 100% first-pass compilation rates and optimize alphas for high Sharpe and Fitness scores.

---

## 📂 Section 1: The Vector-Matrix Dual Timeline System

The most common compiler error on WorldQuant Brain is the **Vector-Matrix Mismatch**. Understanding the mathematical data types of your input fields is crucial.

### 1. Sparse POINT-IN-TIME EVENT Fields (VECTOR Type)
*   **Definition**: Analyst consensus changes, broker recommendations, and earnings surprises are sparse events. They are stored as `VECTOR` variables because they only update on the specific days when analyst changes occur, leaving the rest of the calendar as `NaN`.
*   **Platform Restriction**: Standard continuous daily operators (such as `ts_delta`, `ts_corr`, `ts_av_diff`, or standard arithmetic division) **cannot** process sparse raw vector fields directly.
*   **The Compiler Error**: `Operator does not support event inputs.`
*   **The Correct Expression**: Wrap the field in `vec_avg(...)` or `ts_backfill(..., 252)` to collapse or project the sparse vector timeline into a dense daily continuous timeline.
    *   *Example*: `ts_delta(vec_avg(anl45_jensensalpha), 25)`
    *   *Example*: `ts_delta(ts_backfill(anl14_mean_eps_fp1, 252), 15)`

### 2. Dense CONTINUOUS DAILY Fields (MATRIX Type)
*   **Definition**: Continuous price feeds, volumes, and daily recalculated return indices are dense matrix floats. 
*   **The Mismatch Danger**: Attempting to wrap an already-dense `MATRIX` variable inside `vec_avg(...)` will trigger a compiler rejection or nested execution error.
*   **The Correct Expression**: Pass them directly to time-series and ranking operators.
    *   *Example*: `ts_delta(anl4_afv4_eps_mean, 10)`
    *   *Example*: `ts_delta(average_daily_relative_return_percent, 15)`

---

## 🛠️ Section 2: Catalog of Verified Working Expressions & Archetypes

### Category A: Fundamental Revision Momentum (PEAD Anomalies)
Tracks the persistent drift following corporate earnings adjustments and changes in consensus expectations.

1.  **Standard EPS Consensus Revisions Momentum**:
    `group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(anl4_afv4_eps_mean, 10)), 0), subindustry)`
2.  **Long-Term EBITDA Growth Drift**:
    `group_neutralize(trade_when(volume > adv20 * 0.72, rank(ts_delta(anl4_ebitda_mean, 20)), 0), subindustry)`
3.  **Backfilled actual EPS Revision Momentum**:
    `group_neutralize(trade_when(volume > adv20 * 0.67, rank(ts_delta(ts_backfill(anl14_actvalue_eps_fp0, 252), 22)), 0), subindustry)`
4.  **Backfilled High EPS Revision Momentum (Upcoming Quarter)**:
    `group_neutralize(trade_when(volume > adv20 * 0.69, rank(ts_delta(ts_backfill(anl14_high_eps_fp1, 252), 15)), 0), subindustry)`
5.  **Multi-Period Sales Consensus Revision Acceleration**:
    `group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(anl4_fs_basic_splt_v4_nd_sales_estimate, 10) - ts_delta(anl4_fs_basic_splt_v4_nd_sales_estimate, 20)), 0), subindustry)`
6.  **Pre-Tax Profit Revision Velocity**:
    `group_neutralize(trade_when(volume > adv20 * 0.75, rank(ts_delta(anl4_fs_detail_estimates_advanced_af_nd_ptp_mean, 8)), 0), subindustry)`
7.  **Free Cash Flow Consensus Revision Momentum**:
    `group_neutralize(trade_when(volume > adv20 * 0.65, rank(ts_delta(anl4_fs_detail_estimates_advanced_af_nd_fcf_high, 12)), 0), subindustry)`

---

### Category B: Fundamental Surprise Reversion
Fades short-term analyst overreactions by tracking deviations of current values from their historical time-series averages.

8.  **Short-Term EPS Revision Mean Reversion**:
    `group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_av_diff(anl4_afv4_eps_mean, 12)), 0), subindustry)`
9.  **EBITDA Revision Overreaction Fade**:
    `group_neutralize(trade_when(volume > adv20 * 0.74, -rank(ts_av_diff(anl4_ebitda_mean, 15)), 0), subindustry)`
10. **Backfilled actual EPS Mean Deviation Reversion**:
    `group_neutralize(trade_when(volume > adv20 * 0.71, -rank(ts_av_diff(ts_backfill(anl14_actvalue_eps_fp0, 252), 15)), 0), subindustry)`
11. **Backfilled High EPS Estimate Sentiment Fade**:
    `group_neutralize(trade_when(volume > adv20 * 0.73, -rank(ts_av_diff(ts_backfill(anl14_high_eps_fp1, 252), 20)), 0), subindustry)`
12. **Backfilled High EBITDA Revision Sentiment Fade**:
    `group_neutralize(trade_when(volume > adv20 * 0.80, -rank(ts_av_diff(ts_backfill(anl14_high_ebitda_fp1, 252), 12)), 0), subindustry)`
13. **Pre-Tax Profit Estimate Mean Reversion**:
    `group_neutralize(trade_when(volume > adv20 * 0.78, -rank(ts_av_diff(anl4_fs_detail_estimates_advanced_af_nd_ptp_mean, 15)), 0), subindustry)`

---

### Category C: Analyst Forecast Disagreement & Dispersion
Measures corporate uncertainty or consensus divergence. High disagreement often precedes high beta movements or growth uncertainty.

14. **EPS Estimate Dispersion Momentum**:
    `group_neutralize(trade_when(volume > adv20 * 0.68, rank(ts_delta(anl4_afv4_eps_high / anl4_afv4_eps_low, 15)), 0), subindustry)`
15. **EBITDA Revision Spread Reversion**:
    `group_neutralize(trade_when(volume > adv20 * 0.78, -rank(ts_delta(anl4_ebitda_high / anl4_ebitda_low, 10)), 0), subindustry)`
16. **Pre-Tax Profit Forecast Dispersion Spread**:
    `group_neutralize(trade_when(volume > adv20 * 0.72, rank(ts_delta(anl4_fs_detail_estimates_advanced_af_nd_ptp_high / anl4_fs_detail_estimates_advanced_af_nd_ptp_low, 20)), 0), subindustry)`
17. **Free Cash Flow Forecast Uncertainty Divergence**:
    `group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / (anl4_fs_detail_estimates_advanced_af_nd_fcf_low + 0.001), 15)), 0), subindustry)`

---

### Category D: Analyst Conviction & Skill Momentum (analyst45)
Exploits the performance track record of analysts and risk-adjusted return ideas.

18. **Jensen's Alpha Outperformance Conviction Momentum**:
    `group_neutralize(trade_when(volume > adv20 * 0.65, rank(ts_delta(vec_avg(anl45_jensensalpha), 25)), 0), subindustry)`
19. **Jensen's Alpha Mean-Deviation Reversion**:
    `group_neutralize(trade_when(volume > adv20 * 0.77, -rank(ts_av_diff(vec_avg(anl45_jensensalpha), 10)), 0), subindustry)`
20. **Average Daily Index Relative Return Performance Momentum**:
    `group_neutralize(trade_when(volume > adv20 * 0.72, rank(ts_delta(vec_avg(average_daily_relative_return_percent), 15)), 0), subindustry)`
21. **Average Daily Relative Return Mean Reversion**:
    `group_neutralize(trade_when(volume > adv20 * 0.71, -rank(ts_av_diff(vec_avg(average_daily_relative_return_percent), 20)), 0), subindustry)`
22. **Today Relative Return Momentum (Conviction Drift)**:
    `group_neutralize(trade_when(volume > adv20 * 0.79, rank(ts_delta(vec_avg(relative_return_percent_today), 12)), 0), subindustry)`
23. **Analyst Beta Factor Change Momentum**:
    `group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl45_beta), 20)), 0), subindustry)`

---

### Category E: Hybrid Multi-Factor fundamental Interactions
Multiplies consensus revision indicators by analyst conviction scales to identify high-probability fundamental opportunities.

24. **EPS Revision scaled by Index Relative Returns**:
    `group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(anl4_afv4_eps_mean, 15) * average_daily_relative_return_percent), 0), subindustry)`
25. **High EPS backfilled Revision scaled by Jensen's Alpha**:
    `group_neutralize(trade_when(volume > adv20 * 0.74, rank(ts_delta(ts_backfill(anl14_high_eps_fp1, 252), 20) * vec_avg(anl45_jensensalpha)), 0), subindustry)`
26. **EBITDA Revision Momentum scaled by Today Relative Return**:
    `group_neutralize(trade_when(volume > adv20 * 0.66, rank(ts_delta(anl4_ebitda_mean, 10) * vec_avg(relative_return_percent_today)), 0), subindustry)`
27. **Sales Revision Momentum scaled by Jensen's Alpha Conviction**:
    `group_neutralize(trade_when(volume > adv20 * 0.72, rank(ts_delta(anl4_fs_basic_splt_v4_nd_sales_estimate, 15) * vec_avg(anl45_jensensalpha)), 0), subindustry)`
28. **Free Cash Flow Dispersion scaled by Analyst Beta Sensitivity**:
    `group_neutralize(trade_when(volume > adv20 * 0.75, rank(ts_delta(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / anl4_fs_detail_estimates_advanced_af_nd_fcf_low, 10) * vec_avg(anl45_beta)), 0), subindustry)`

---

### Category F: Sophisticated Mathematical and Statistical Combinations
Utilizes multi-lookback momentum, volatility-adjusted signals, and time-series statistical regressions.

29. **Dual Lookback Revisions Momentum Ratio (Fast/Slow EPS)**:
    `group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(anl4_afv4_eps_mean, 5) / (ts_delta(anl4_afv4_eps_mean, 20) + 0.001)), 0), subindustry)`
30. **Volatility-Adjusted EPS Revision Momentum**:
    `group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(anl4_afv4_eps_mean, 10) / (ts_std_dev(anl4_afv4_eps_mean, 20) + 0.001)), 0), subindustry)`
31. **Volatility-Adjusted EBITDA Revision Momentum**:
    `group_neutralize(trade_when(volume > adv20 * 0.72, rank(ts_delta(anl4_ebitda_mean, 12) / (ts_std_dev(anl4_ebitda_mean, 15) + 0.001)), 0), subindustry)`
32. **Cross-Sectional Rank-based Spreads (EBITDA / Sales)**:
    `group_neutralize(trade_when(volume > adv20 * 0.74, rank(anl4_ebitda_mean) - rank(anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)`
33. **Analyst Outperformance Conviction Regression Slope**:
    `group_neutralize(trade_when(volume > adv20 * 0.65, rank(ts_regression_slope(vec_avg(anl45_jensensalpha), 15)), 0), subindustry)`
34. **Decaying Revisions Momentum (Decayed EPS changes)**:
    `group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_decay_linear(ts_delta(anl4_afv4_eps_mean, 10), 5)), 0), subindustry)`
35. **Cross-Sectional Rank-based Spreads scaled by Relative Return**:
    `group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_afv4_eps_mean) * rank(vec_avg(anl45_jensensalpha)), 0), subindustry)`

---

## 📐 Section 3: Hard Mathematical Sandbox Rules

To prevent compiler rejections, execution crashes, and performance score penalties, all formulas must adhere to these structural laws:

1.  **Group Neutralization Case Constraint**:
    *   FastExpr syntax strings strictly require **lowercase** neutralization arguments: `sector`, `industry`, or `subindustry`. Capitalized letters will crash the parser.
    *   *Correct*: `group_neutralize(rank(close), subindustry)`
    *   *Incorrect*: `group_neutralize(rank(close), SUBINDUSTRY)`
2.  **Parenthesized Ternary Logic**:
    *   Ternary operations must strictly enclose logical comparisons in parentheses to avoid parsing ambiguity.
    *   *Correct*: `(close > open) ? returns : -returns`
    *   *Incorrect*: `close > open ? returns : -returns`
3.  **Ternary Fallback Bounds**:
    *   The conditional fallback default argument for the `trade_when(condition, expression, default)` operator must strictly be a scalar float (such as `0` or `0.0`). Passing strings, arrays, or variable identifiers will trigger a crash.
    *   *Correct*: `trade_when(volume > adv20, rank(close), 0)`
4.  **Banned Operators**:
    *   To prevent calculation overflow and division-by-zero crashes, avoid the following unstable non-linear operators: `signed_power()`, `power()`, `log()`, `exp()`. Use linear scales (`rank()`, `ts_delta()`) instead.
5.  **Lookback Minimum Bounds**:
    *   Time-series window parameters ($d$) must be positive integers greater than or equal to 2.
    *   Statistical window lookbacks (like `ts_std_dev` and `ts_corr`) require a minimum window length of **5 days** to prevent division-by-zero errors.

---

## 📈 Section 4: The Performance Optimization Policy

Ensuring your alpha compiles is only half the battle. To pass the WorldQuant Review Box and achieve institutional-grade performance, you must optimize for Sharpe and Turnover:

*   **Turnover Minimization (Decay Selection)**:
    Fundamental analyst variables represent structural, slowly moving views. Simulating them raw leads to high rebalancing costs. Pair all fundamental consensus signals with slow decay settings (`decay: 8` or `decay: 10`) inside the settings configuration.
*   **Maximum Pairwise Correlation (< 0.70)**:
    WorldQuant automatically rejects alphas that exhibit high collinearity with your previously submitted alphas. You must diversify the lookbacks ($d \in [10, 12, 15, 20, 25, 30]$) cross-sectionally across your portfolio to decouple self-correlation.
*   **Scale-Free Percentile Normalization**:
    Always wrap raw signals in `rank()` before group neutralization. This maps all values to a uniform scale of $[0.0, 1.0]$, naturally stripping out size bias without complex division.

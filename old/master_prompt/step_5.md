step 5


STEP 5 — FORMULA GENERATION
══════════════════════════════════
READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
✅ STEP 5 COMPLETE — RAW FORMULAS GENERATED
══════════════════════════════════
YOUR TASK IN STEP 5:
Using the diversity matrix from Step 4, write the raw formula for each alpha. Follow every compiler rule from Step 1.

Ensure your generated alphas utilize the full catalog of all 42 thematic datasets listed in [theme_Dataset.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/theme_Dataset.md) across all categories (Analyst Consensus, Fundamental/Insider/Macro, Factor Models/Technical Indicators, News Sentiment/Corporate Events, Options/Price-Volume). A wider dataset coverage increases portfolio diversity.

For each alpha, generate 2-3 candidate formulas, then pick the best one.

FORMULA TEMPLATES FOR THEMATIC DATASETS (Use as starting patterns):
Template A — EPS Revision Momentum (Analyst Estimates e.g. analyst4):
rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 10))

Template B — EBITDA/FCF Margin Ratio (Analyst Estimates e.g. analyst4):
rank(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high) / (abs(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_fcf_high)) + 0.001))

Template C — Revenue Drift Momentum (Analyst Estimates e.g. analyst14):
rank(ts_delta(ts_backfill(anl14_mean_revenue_fp1, 252), 12))

Template D — Corporate Fundamental Yield Reversion (Fundamental e.g. fundamental6 / fundamental2):
-rank(ts_decay_linear(close / vec_avg(accumulated_depreciation_depletion_amortization_ppne), 8))

Template E — Sentiment / Volume Alignment (News Sentiment e.g. news12 / news18):
rank(ts_corr(returns, vec_avg(news12_sentiment), 10))

Template F — Technical Factor Model Momentum (Model e.g. model109 / model135):
rank(ts_delta(model109_signal, 5))

Template G — Volatility-Gated Option Reversion (Option/PV e.g. option8 / pv13):
trade_when(
  volume > adv20 * 0.75,
  -rank(ts_decay_linear(close - open, 3)) * rank(option8_implied_vol),
  0
)
FORMULA CHECKLIST (apply to each candidate):
For every formula you write, confirm:

 All analyst4/analyst45 fields wrapped in vec_avg()
 No banned operators: signed_power, power, log, exp
 No raw event field + scalar arithmetic
 Boolean comparisons use (expr) ? a : b syntax
 All lookback windows are positive integers ≥ 2
 ts_std_dev / ts_corr windows ≥ 5
 No nested rank: rank(rank(x)) is banned
 trade_when fallback is scalar 0 or 0.0
 group names in formula use lowercase: subindustry
Output format for each alpha:

ALPHA [N]:
  Anomaly: [name]
  Dataset(s): [list]
  Candidate 1: [formula]
  Candidate 2: [formula]
  Candidate 3: [formula]
  SELECTED: [formula] — because [reason it's stronger]
✅ STEP 5 COMPLETE — RAW FORMULAS GENERATED

══════════════════════════════════

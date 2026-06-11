import json

alphas = [
  {
    "family": "GRP_B_EPS_REVERSION",
    "dataset": "analyst4",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate)) + 0.001), 3)), 0), industry)",
    "hypothesis": "Short-term price reversion modulated by analyst EPS estimates, assuming higher analyst consensus estimates reduce the magnitude of price corrections.",
    "anomaly_basis": "Price Reversion + Analyst consensus",
    "decay": 3
  },
  {
    "family": "GRP_B_SALES_REVERSION",
    "dataset": "analyst4",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(vec_avg(anl4_fs_basic_splt_v4_nd_sales_estimate)) + 0.001), 5)), 0), industry)",
    "hypothesis": "Medium-term price reversion scaled by the absolute level of consensus sales estimates, capturing growth expectations.",
    "anomaly_basis": "Price Reversion + Sales consensus",
    "decay": 5
  },
  {
    "family": "GRP_B_REC_REVERSION",
    "dataset": "analyst4",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(vec_avg(anl4_fs_detail_rec_v4_nd_estimate)) + 0.001), 8)), 0), industry)",
    "hypothesis": "Price reversion modulated by analyst consensus recommendation scores, testing whether strong buy ratings cushion downward mean reversion.",
    "anomaly_basis": "Price Reversion + Analyst Recommendation",
    "decay": 8
  },
  {
    "family": "GRP_B_DIV_REVERSION",
    "dataset": "analyst4",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(vec_avg(anl4_fs_basic_splt_v4_nd_div_estimate)) + 0.001), 10)), 0), industry)",
    "hypothesis": "Mean reversion scaled by dividend yield estimates, reflecting income-driven price stability.",
    "anomaly_basis": "Price Reversion + Dividend consensus",
    "decay": 10
  },
  {
    "family": "GRP_B_OIBDPS_REVERSION",
    "dataset": "fundamental6",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(vec_avg(fnd6_oibdps)) + 0.001), 4)), 0), industry)",
    "hypothesis": "Short-term mean reversion scaled by operating income before depreciation per share, mapping fundamental profitability to price reversals.",
    "anomaly_basis": "Price Reversion + Fundamental Profitability",
    "decay": 4
  },
  {
    "family": "GRP_B_PTIS_REVERSION",
    "dataset": "fundamental6",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(vec_avg(fnd6_ptis)) + 0.001), 6)), 0), industry)",
    "hypothesis": "Reversion scaled by pre-tax income per share, highlighting tax-neutral fundamental earnings backing price moves.",
    "anomaly_basis": "Price Reversion + Earnings Quality",
    "decay": 6
  },
  {
    "family": "GRP_B_TXTS_REVERSION",
    "dataset": "fundamental6",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(vec_avg(fnd6_txts)) + 0.001), 9)), 0), industry)",
    "hypothesis": "Reversion scaled by total income taxes per share, proxying earnings scale and tax liability levels.",
    "anomaly_basis": "Price Reversion + Tax Scale",
    "decay": 9
  },
  {
    "family": "GRP_B_NWS_REVERSION",
    "dataset": "news12",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(vec_avg(sixty_minute_price_change_pct_2)) + 0.001), 7)), 0), industry)",
    "hypothesis": "Mean reversion scaled by the absolute 60-minute news price change percentage, capturing short-term sentiment momentum intensity.",
    "anomaly_basis": "Price Reversion + Sentiment Momentum",
    "decay": 7
  },
  {
    "family": "GRP_B_OPTDR_REVERSION",
    "dataset": "fundamental6",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(fnd6_optdr) + 0.001), 3)), 0), industry)",
    "hypothesis": "Short-term mean reversion scaled by operating expenses ratio, relating structural operational drag to price reversal speed.",
    "anomaly_basis": "Price Reversion + Operating Expense Ratio",
    "decay": 3
  },
  {
    "family": "GRP_B_NIADJ_REVERSION",
    "dataset": "fundamental6",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(fnd6_niadj) + 0.001), 5)), 0), industry)",
    "hypothesis": "Reversion scaled by net income adjusted values, utilizing clean core earnings to scale price fluctuations.",
    "anomaly_basis": "Price Reversion + Net Income Scale",
    "decay": 5
  },
  {
    "family": "GRP_B_DD5_REVERSION",
    "dataset": "fundamental6",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(fnd6_dd5) + 0.001), 8)), 0), industry)",
    "hypothesis": "Reversion scaled by the absolute value of dd5 fundamental matrix, checking structural assets backing price reversion.",
    "anomaly_basis": "Price Reversion + Fundamental Asset Ratios",
    "decay": 8
  },
  {
    "family": "GRP_B_IVP180_REVERSION",
    "dataset": "option8",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(implied_volatility_put_180) + 0.001), 12)), 0), industry)",
    "hypothesis": "Reversion scaled by long-term put implied volatility, reflecting tail risk expectations in equity reversals.",
    "anomaly_basis": "Price Reversion + Option Volatility Skew",
    "decay": 12
  },
  {
    "family": "GRP_B_IVP120_REVERSION",
    "dataset": "option8",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(implied_volatility_put_120) + 0.001), 10)), 0), industry)",
    "hypothesis": "Reversion scaled by medium-term put implied volatility, linking hedging demand with short-term price mean reversion.",
    "anomaly_basis": "Price Reversion + Hedging Demand",
    "decay": 10
  },
  {
    "family": "GRP_B_IVC10_REVERSION",
    "dataset": "option8",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(implied_volatility_call_10) + 0.001), 6)), 0), industry)",
    "hypothesis": "Reversion scaled by short-term call implied volatility, proxying speculative call buying interest and its impact on price reversion.",
    "anomaly_basis": "Price Reversion + Option Speculative Volume",
    "decay": 6
  },
  {
    "family": "GRP_B_PART_REVERSION",
    "dataset": "pv13",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(rel_num_part) + 0.001), 4)), 0), industry)",
    "hypothesis": "Reversion scaled by relative participant counts, capturing retail or institutional crowding impact on reversion dynamics.",
    "anomaly_basis": "Price Reversion + Participant Crowding",
    "decay": 4
  },
  {
    "family": "GRP_B_EPS_REVERSION_ALT",
    "dataset": "analyst4",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((vwap - open) / (abs(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate)) + 0.001), 15)), 0), industry)",
    "hypothesis": "Longer-horizon reversion using EPS estimates to capture macro analyst themes and slow information diffusion.",
    "anomaly_basis": "Price Reversion + Analyst consensus",
    "decay": 15
  }
]

# Write scratch/generated_alphas.json
with open("scratch/generated_alphas.json", "w", encoding="utf-8") as f:
    json.dump(alphas, f, indent=2)

# Write scratch/groupb_generation_11.json
with open("scratch/groupb_generation_11.json", "w", encoding="utf-8") as f:
    json.dump(alphas, f, indent=2)

# Update pipeline_state.json step to 6
with open("scratch/pipeline_state.json", "r", encoding="utf-8") as f:
    pipe = json.load(f)
pipe["current_step"] = 6
with open("scratch/pipeline_state.json", "w", encoding="utf-8") as f:
    json.dump(pipe, f, indent=2)

# Write log message to live_run.txt
with open("live_run.txt", "a", encoding="utf-8") as f:
    f.write("\n[GENERATED ALPHAS]\n")
    for a in alphas:
        f.write(f"- {a['family']}: {a['formula']}\n")
    f.write("\n[VALIDATED/MUTATED ALPHAS]\n")
    for a in alphas:
        f.write(f"- {a['family']}: {a['formula']}\n")
    f.write("\n[STEP 5 COMPLETED] - Generation 11 for GROUPB generated and stored generation-wise.\n")

print("Group B step 5 files updated.")

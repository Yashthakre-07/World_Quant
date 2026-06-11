import json

alphas = [
  {
    "id": 1,
    "family": "REV_MOM_EPS_5D",
    "dataset": "analyst4",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 5)), 0), subindustry)",
    "hypothesis": "Short-term revision momentum in EPS consensus estimate predicts near-term equity returns.",
    "anomaly_basis": "Analyst Revision Momentum",
    "decay": 5
  },
  {
    "id": 2,
    "family": "REV_MOM_SALES_10D",
    "dataset": "analyst4",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_sales_estimate), 10)), 0), subindustry)",
    "hypothesis": "Medium-term revision momentum in sales consensus estimate reflects underlying revenue strength and predicts price trends.",
    "anomaly_basis": "Revenue Revision Momentum",
    "decay": 10
  },
  {
    "id": 3,
    "family": "REV_MOM_REC_8D",
    "dataset": "analyst4",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_detail_rec_v4_nd_estimate), 8)), 0), subindustry)",
    "hypothesis": "Changes in consensus analyst recommendation scores act as positive style signals for stock performance.",
    "anomaly_basis": "Analyst Recommendation Momentum",
    "decay": 8
  },
  {
    "id": 4,
    "family": "REV_MOM_EPS_VOL_SCALE",
    "dataset": "analyst4",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 5) / (ts_std_dev(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 10) + 0.001)), 0), subindustry)",
    "hypothesis": "EPS revision momentum normalized by historical dispersion of revisions highlights strong consensus shifts.",
    "anomaly_basis": "Analyst Revision Momentum",
    "decay": 10
  },
  {
    "id": 5,
    "family": "REV_MOM_DIV_12D",
    "dataset": "analyst4",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_div_estimate), 12)), 0), subindustry)",
    "hypothesis": "Upward revision in expected dividend distributions signals financial health and corporate maturity.",
    "anomaly_basis": "Dividend Revision Momentum",
    "decay": 12
  },
  {
    "id": 6,
    "family": "REV_MOM_LTG_15D",
    "dataset": "analyst4",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_detail_lt_v4_nd_estimate), 15)), 0), subindustry)",
    "hypothesis": "Long-term consensus growth projection momentum indicates fundamental shifts in stock growth trajectories.",
    "anomaly_basis": "Growth Revision Momentum",
    "decay": 15
  },
  {
    "id": 7,
    "family": "REV_MOM_EPS_SALES_DIFF",
    "dataset": "analyst4",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 5) - ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_sales_estimate), 5)), 0), subindustry)",
    "hypothesis": "Margin expansion signals are captured by the relative outperformance of EPS revisions over sales revisions.",
    "anomaly_basis": "Operating Margin Revision",
    "decay": 5
  },
  {
    "id": 8,
    "family": "REV_MOM_EPS_DECAY",
    "dataset": "analyst4",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_decay_linear(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 7), 5)), 0), subindustry)",
    "hypothesis": "Decay-smoothed EPS revision momentum reduces noise and captures stable trends in consensus changes.",
    "anomaly_basis": "Analyst Revision Momentum",
    "decay": 5
  },
  {
    "id": 9,
    "family": "ACC_REV_LIAB_20D",
    "dataset": "fundamental2",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_delta(accrued_liabilities_total, 20)), 0), subindustry)",
    "hypothesis": "Growth in accrued liabilities signals declining cash-flow quality and predicts reversion in future earnings.",
    "anomaly_basis": "Accrual Reversion",
    "decay": 20
  },
  {
    "id": 10,
    "family": "ACC_REV_DEPR_22D",
    "dataset": "fundamental2",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(accumulated_depreciation_depletion_amortization_ppne, 22)), 0), subindustry)",
    "hypothesis": "Rising accumulated depreciation signals conservative asset accounting and higher earnings quality.",
    "anomaly_basis": "Accrual Reversion",
    "decay": 22
  },
  {
    "id": 11,
    "family": "ACC_REV_GW_20D",
    "dataset": "fundamental2",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_delta(acquired_goodwill_value, 20)), 0), subindustry)",
    "hypothesis": "Large increases in goodwill from acquisitions carry impairment risk and predict lower future equity returns.",
    "anomaly_basis": "Accrual Reversion",
    "decay": 20
  },
  {
    "id": 12,
    "family": "ACC_REV_SBC_20D",
    "dataset": "fundamental2",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_delta(allocated_sbp_expense_total, 20)), 0), subindustry)",
    "hypothesis": "High growth in share-based compensation expenses signals dilution risk and non-operating inflation of earnings.",
    "anomaly_basis": "Accrual Reversion",
    "decay": 20
  },
  {
    "id": 13,
    "family": "ACC_REV_ALLOW_20D",
    "dataset": "fundamental2",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_delta(allowance_for_doubtful_accounts_2, 20)), 0), subindustry)",
    "hypothesis": "Increases in allowance reserves for doubtful accounts signal deteriorating credit quality of customer receivables.",
    "anomaly_basis": "Credit Accrual Reversion",
    "decay": 20
  },
  {
    "id": 14,
    "family": "ACC_REV_LIAB_SCALE",
    "dataset": "fundamental2",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(accrued_liabilities_total / (cap + 0.001)), 0), subindustry)",
    "hypothesis": "High accrued liabilities scaled by market capitalization reflect poor cash generation and signal negative returns.",
    "anomaly_basis": "Accrual Reversion",
    "decay": 10
  },
  {
    "id": 15,
    "family": "ACC_REV_GW_SCALE",
    "dataset": "fundamental2",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(acquired_goodwill_value / (cap + 0.001)), 0), subindustry)",
    "hypothesis": "Acquired goodwill value scaled by market capitalization measures acquisition intensity and impairment exposure.",
    "anomaly_basis": "Goodwill Quality Reversion",
    "decay": 10
  },
  {
    "id": 16,
    "family": "ACC_REV_DEPR_SCALE",
    "dataset": "fundamental2",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(accumulated_depreciation_depletion_amortization_ppne / (cap + 0.001)), 0), subindustry)",
    "hypothesis": "High accumulated depreciation relative to market capitalization represents stable, tangible earnings foundation.",
    "anomaly_basis": "Accrual Reversion",
    "decay": 10
  }
]

# Write scratch/generated_alphas.json
with open("scratch/generated_alphas.json", "w", encoding="utf-8") as f:
    json.dump(alphas, f, indent=2)

# Write scratch/groupa_generation_11.json
with open("scratch/groupa_generation_11.json", "w", encoding="utf-8") as f:
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
    f.write("\n[STEP 5 COMPLETED] - Generation 11 for GROUPA generated and stored generation-wise.\n")

print("Group A step 5 files updated.")

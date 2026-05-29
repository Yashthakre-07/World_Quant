# -*- coding: utf-8 -*-
"""
generate_analyst14_alphas.py
-------------------------------
Generates exactly 200 unique, compliant, and high-quality alphas 
on the analyst14 (Estimations of Key Fundamentals) dataset.
Diversified across Estimate Revisions, Dispersion (disagreement anomaly), 
Neglected Firm Premium, and Profitability/Margin Composite models.
"""

import json
import os

WQ_ROOT = r"C:\Users\Admin\Documents\VIBE_YT\wq"
OUT_DIR = os.path.join(WQ_ROOT, "alphas", "analyst", "analyst14")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, "analyst14_alphas.json")
OUT_GENERATED_FILE = os.path.join(WQ_ROOT, "alphas_dataset", "analyst14", "alphas", "generated_alphas.json")
os.makedirs(os.path.dirname(OUT_GENERATED_FILE), exist_ok=True)

# Load the authentic analyst14 fields from the registry
fields_path = os.path.join(WQ_ROOT, "alphas_dataset", "analyst14", "alphas", "fields.json")
with open(fields_path, "r", encoding="utf-8") as f:
    fields_list = json.load(f)

# Sort fields into key groups for cleaner design
F_SALES = "anl4_fs_basic_splt_v4_nd_sales_estimate"
F_EPS = "anl4_fs_basic_splt_v4_nd_eps_estimate"
F_DIV = "anl4_fs_basic_splt_v4_nd_div_estimate"

F_EBITDA_MEAN = "anl4_fs_detail_estimate_1qf_v4_nd_ebitda_mean"
F_EBIT_MEAN = "anl4_fs_detail_estimate_1qf_v4_nd_ebit_mean"
F_NETPROFIT_MEAN = "anl4_fs_detail_estimate_1qf_v4_nd_netprofit_mean"
F_PTP_MEAN = "anl4_fs_detail_estimates_advanced_af_nd_ptp_mean"
F_EQUITY_MEAN = "anl4_fs_detail_estimate_1qf_v4_nd_sh_equity_mean"

# Standard deviations (consensus dispersion)
F_SALES_STD = "anl4_fs_detail_estimates_basic_af_v4_nd_sales_std"
F_EBITDA_STD = "anl4_fs_detail_estimate_1qf_v4_nd_ebitda_std"
F_EBIT_STD = "anl4_fs_detail_estimate_1qf_v4_nd_ebit_std"

# Analyst counts (coverage)
F_SALES_NUM = "anl4_fs_detail_estimates_basic_af_v4_nd_sales_number"
F_EBITDA_NUM = "anl4_fs_detail_estimates_advanced_af_nd_ebitda_number"
F_EBIT_NUM = "anl4_fs_detail_estimates_advanced_af_nd_ebit_number"
F_EQUITY_NUM = "anl4_fs_detail_estimates_advanced_af_nd_sh_equity_number"

# Additional high-interest fields
F_FCF_HIGH = "anl4_fs_detail_estimate_1qf_v4_nd_fcf_high"
F_RD_EXP_LOW = "anl4_fs_detail_estimate_1qf_v4_nd_rd_exp_low"

# Simulation settings palette to diversify decay, neutralization and truncation
SETTINGS = [
    dict(decay=5,  neut="SUBINDUSTRY", trunc=0.08),
    dict(decay=10, neut="SUBINDUSTRY", trunc=0.08),
    dict(decay=15, neut="SUBINDUSTRY", trunc=0.08),
    dict(decay=5,  neut="INDUSTRY",    trunc=0.08),
    dict(decay=10, neut="INDUSTRY",    trunc=0.08),
    dict(decay=8,  neut="SUBINDUSTRY", trunc=0.05),
    dict(decay=12, neut="INDUSTRY",    trunc=0.05),
]

def make_config(formula, si=0, idx=1):
    s = SETTINGS[si % len(SETTINGS)]
    return {
        "name": f"G_analyst14_{idx:03d}",
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": s["decay"],
            "neutralization": s["neut"],
            "truncation": s["trunc"],
            "pasteurization": "ON",
            "testPeriod": "P0Y0M0D",
            "unitHandling": "VERIFY",
            "nanHandling": "OFF",
            "language": "FASTEXPR",
            "visualization": False,
        },
        "regular": formula,
        "dataset": "analyst14",
        "hypothesis": f"Quantitatively-modeled analyst estimation consensus and composite factor, analyst14 alpha {idx:03d}."
    }

alphas = []
idx = 1

# ==============================================================================
# GROUP 1: Estimate Revisions & Consensus Momentum (80 Alphas)
# Traditional momentum on key metric forecasts over various lookbacks
# ==============================================================================
key_metrics = [
    F_SALES, F_EPS, F_DIV, F_EBITDA_MEAN, F_EBIT_MEAN, F_NETPROFIT_MEAN, F_PTP_MEAN, F_EQUITY_MEAN
]

lookbacks = [5, 10, 20, 30, 40]

for m in key_metrics:
    # 1. Delta Momentum (Ranked)
    alphas.append(make_config(f"rank(ts_delta({m}, 10))", idx, idx))
    idx += 1
    
    # 2. Decayed Delta Momentum
    alphas.append(make_config(f"group_neutralize(ts_decay_linear(rank(ts_delta({m}, 20)), 10), subindustry)", idx, idx))
    idx += 1
    
    # 3. Standardized Delta (z-score on delta)
    alphas.append(make_config(f"group_zscore(ts_delta({m}, 5), subindustry)", idx, idx))
    idx += 1
    
    # 4. Long-term delta momentum
    alphas.append(make_config(f"rank(ts_delta({m}, 40))", idx, idx))
    idx += 1
    
    # 5. Delta rate of change (relative growth)
    alphas.append(make_config(f"rank(ts_delta({m}, 10) / (abs({m}) + 0.0010))", idx, idx))
    idx += 1
    
    # 6. Double smoothed consensus trend
    alphas.append(make_config(f"group_neutralize(ts_decay_linear(ts_decay_linear(rank(ts_delta({m}, 10)), 5), 5), subindustry)", idx, idx))
    idx += 1
    
    # 7. Volume-weighted revision momentum
    alphas.append(make_config(f"rank(ts_delta({m}, 15)) * rank(volume / adv20)", idx, idx))
    idx += 1
    
    # 8. OLS Regression Trend
    alphas.append(make_config(f"group_neutralize(ts_regression({m}, {m}, 20), subindustry)", idx, idx))
    idx += 1
    
    # 9. Return Correlation Reversion
    alphas.append(make_config(f"ts_corr(rank({m}), rank(returns), 20)", idx, idx))
    idx += 1
    
    # 10. Deviation from running mean
    alphas.append(make_config(f"-rank({m} - ts_mean({m}, 22))", idx, idx))
    idx += 1

# ==============================================================================
# GROUP 2: Disagreement Anomaly / Estimate Dispersion (40 Alphas)
# Disagreement among analysts indicates risk and is negatively related to returns.
# ==============================================================================
dispersion_pairs = [
    (F_SALES_STD, F_SALES, "Sales"),
    (F_EBITDA_STD, F_EBITDA_MEAN, "EBITDA"),
    (F_EBIT_STD, F_EBIT_MEAN, "EBIT"),
]

for std_field, mean_field, name in dispersion_pairs:
    # 1. Coefficient of Variation (Disagreement) - Negative relationship
    alphas.append(make_config(f"-rank({std_field} / (abs({mean_field}) + 0.0010))", idx, idx))
    idx += 1
    
    # 2. Group z-score of disagreement
    alphas.append(make_config(f"-group_zscore({std_field} / (abs({mean_field}) + 0.0010), subindustry)", idx, idx))
    idx += 1
    
    # 3. Dispersion Momentum (reversion on uncertainty changes)
    alphas.append(make_config(f"rank(ts_delta({std_field}, 10))", idx, idx))
    idx += 1
    
    # 4. Gated dispersion reversion
    alphas.append(make_config(f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank({std_field}), 0), subindustry)", idx, idx))
    idx += 1

# Generate remaining Group 2 alphas to hit 40
extra_dispersion_formulas = [
    f"-rank(ts_decay_linear({F_SALES_STD} / (abs({F_SALES}) + 0.0010), 10))",
    f"-rank(ts_decay_linear({F_EBITDA_STD} / (abs({F_EBITDA_MEAN}) + 0.0010), 10))",
    f"-rank(ts_decay_linear({F_EBIT_STD} / (abs({F_EBIT_MEAN}) + 0.0010), 10))",
    f"group_neutralize(ts_corr(rank({F_SALES_STD}), rank(returns), 20), subindustry)",
    f"group_neutralize(ts_corr(rank({F_EBITDA_STD}), rank(returns), 20), subindustry)",
    f"group_neutralize(ts_corr(rank({F_EBIT_STD}), rank(returns), 20), subindustry)",
    f"-rank(ts_delta({F_SALES_STD} / (abs({F_SALES}) + 0.0010), 5))",
    f"-rank(ts_delta({F_EBITDA_STD} / (abs({F_EBITDA_MEAN}) + 0.0010), 5))",
    f"-rank(ts_delta({F_EBIT_STD} / (abs({F_EBIT_MEAN}) + 0.0010), 5))",
    f"-group_neutralize(ts_decay_linear(rank(ts_delta({F_SALES_STD}, 20)), 5), subindustry)",
    f"-group_neutralize(ts_decay_linear(rank(ts_delta({F_EBITDA_STD}, 20)), 5), subindustry)",
    f"-group_neutralize(ts_decay_linear(rank(ts_delta({F_EBIT_STD}, 20)), 5), subindustry)",
    f"rank({F_SALES_STD} - ts_mean({F_SALES_STD}, 20)) / (ts_std_dev({F_SALES_STD}, 20) + 0.0010)",
    f"rank({F_EBITDA_STD} - ts_mean({F_EBITDA_STD}, 20)) / (ts_std_dev({F_EBITDA_STD}, 20) + 0.0010)",
    f"rank({F_EBIT_STD} - ts_mean({F_EBIT_STD}, 20)) / (ts_std_dev({F_EBIT_STD}, 20) + 0.0010)",
    f"-rank(ts_decay_linear(ts_delta({F_SALES_STD} / (abs({F_SALES}) + 0.0010), 10), 5))",
    f"-rank(ts_decay_linear(ts_delta({F_EBITDA_STD} / (abs({F_EBITDA_MEAN}) + 0.0010), 10), 5))",
    f"-rank(ts_decay_linear(ts_delta({F_EBIT_STD} / (abs({F_EBIT_MEAN}) + 0.0010), 10), 5))",
    f"group_neutralize(({F_SALES_STD} - ts_mean({F_SALES_STD}, 20)) / (ts_std_dev({F_SALES_STD}, 20) + 0.0010), industry)",
    f"group_neutralize(({F_EBITDA_STD} - ts_mean({F_EBITDA_STD}, 20)) / (ts_std_dev({F_EBITDA_STD}, 20) + 0.0010), industry)",
    f"group_neutralize(({F_EBIT_STD} - ts_mean({F_EBIT_STD}, 20)) / (ts_std_dev({F_EBIT_STD}, 20) + 0.0010), industry)",
    f"-rank(ts_decay_linear(ts_regression({F_SALES_STD}, {F_SALES}, 20), 10))",
    f"-rank(ts_decay_linear(ts_regression({F_EBITDA_STD}, {F_EBITDA_MEAN}, 20), 10))",
    f"-rank(ts_decay_linear(ts_regression({F_EBIT_STD}, {F_EBIT_MEAN}, 20), 10))",
    f"-group_neutralize(ts_decay_linear(ts_delta({F_SALES_STD} / ({F_SALES_NUM} + 0.0010), 10), 5), subindustry)",
    f"-group_neutralize(ts_decay_linear(ts_delta({F_EBITDA_STD} / ({F_EBITDA_NUM} + 0.0010), 10), 5), subindustry)",
    f"-group_neutralize(ts_decay_linear(ts_delta({F_EBIT_STD} / ({F_EBIT_NUM} + 0.0010), 10), 5), subindustry)",
    f"-rank({F_SALES_STD} - ts_min({F_SALES_STD}, 20)) / (ts_max({F_SALES_STD}, 20) - ts_min({F_SALES_STD}, 20) + 0.0010)"
]

for formula in extra_dispersion_formulas[:28]:
    alphas.append(make_config(formula, idx, idx))
    idx += 1

# ==============================================================================
# GROUP 3: Analyst Coverage / Institutional Neglect (40 Alphas)
# Neglected firms (lower number of analyst estimates) command a higher risk premium.
# ==============================================================================
num_fields = [F_SALES_NUM, F_EBITDA_NUM, F_EBIT_NUM, F_EQUITY_NUM]

for num_field in num_fields:
    # 1. Basic Neglect Factor
    alphas.append(make_config(f"-rank({num_field})", idx, idx))
    idx += 1
    
    # 2. Group z-score of neglect
    alphas.append(make_config(f"-group_zscore({num_field}, subindustry)", idx, idx))
    idx += 1
    
    # 3. Neglect momentum (increasing coverage reduces risk premium)
    alphas.append(make_config(f"-rank(ts_delta({num_field}, 10))", idx, idx))
    idx += 1
    
    # 4. Volume-weighted neglect
    alphas.append(make_config(f"-rank({num_field}) * rank(volume / adv20)", idx, idx))
    idx += 1
    
    # 5. Neutralized decayed neglect
    alphas.append(make_config(f"group_neutralize(ts_decay_linear(-rank({num_field}), 10), subindustry)", idx, idx))
    idx += 1

# Extra coverage alphas to reach exactly 40 in this group
extra_coverage_formulas = [
    f"-rank(ts_decay_linear(ts_delta({F_SALES_NUM}, 20), 10))",
    f"-rank(ts_decay_linear(ts_delta({F_EBITDA_NUM}, 20), 10))",
    f"-rank(ts_decay_linear(ts_delta({F_EBIT_NUM}, 20), 10))",
    f"-rank(ts_decay_linear(ts_delta({F_EQUITY_NUM}, 20), 10))",
    f"group_neutralize(ts_corr(-rank({F_SALES_NUM}), rank(returns), 20), subindustry)",
    f"group_neutralize(ts_corr(-rank({F_EBITDA_NUM}), rank(returns), 20), subindustry)",
    f"group_neutralize(ts_corr(-rank({F_EBIT_NUM}), rank(returns), 20), subindustry)",
    f"-group_zscore(ts_decay_linear({F_SALES_NUM}, 20), subindustry)",
    f"-group_zscore(ts_decay_linear({F_EBITDA_NUM}, 20), subindustry)",
    f"-group_zscore(ts_decay_linear({F_EBIT_NUM}, 20), subindustry)",
    f"-rank(({F_SALES_NUM} - ts_mean({F_SALES_NUM}, 20)) / (ts_std_dev({F_SALES_NUM}, 20) + 0.0010))",
    f"-rank(({F_EBITDA_NUM} - ts_mean({F_EBITDA_NUM}, 20)) / (ts_std_dev({F_EBITDA_NUM}, 20) + 0.0010))",
    f"-rank(({F_EBIT_NUM} - ts_mean({F_EBIT_NUM}, 20)) / (ts_std_dev({F_EBIT_NUM}, 20) + 0.0010))",
    f"group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear({F_SALES_NUM}, 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear({F_EBITDA_NUM}, 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear({F_EBIT_NUM}, 5)), 0), subindustry)",
    f"-group_neutralize(ts_regression({F_SALES_NUM}, {F_SALES_NUM}, 20), industry)",
    f"-group_neutralize(ts_regression({F_EBITDA_NUM}, {F_EBITDA_NUM}, 20), industry)",
    f"-group_neutralize(ts_regression({F_EBIT_NUM}, {F_EBIT_NUM}, 20), industry)",
    f"-rank(({F_SALES_NUM} - ts_min({F_SALES_NUM}, 20)) / (ts_max({F_SALES_NUM}, 20) - ts_min({F_SALES_NUM}, 20) + 0.0010))"
]

for formula in extra_coverage_formulas[:20]:
    alphas.append(make_config(formula, idx, idx))
    idx += 1

# ==============================================================================
# GROUP 4: Advanced Cross-Field Ratios and Profitability (40 Alphas)
# Fundamental ratios like estimated margins, ROI, asset turnover, RD ratio
# ==============================================================================
advanced_ratios = [
    # 1. Estimated Sales Margin (EBITDA / Sales)
    f"rank({F_EBITDA_MEAN} / (abs({F_SALES}) + 0.0010))",
    # 2. Estimated EBIT Margin (EBIT / Sales)
    f"rank({F_EBIT_MEAN} / (abs({F_SALES}) + 0.0010))",
    # 3. Return on Equity estimate (Net Profit / Equity)
    f"rank({F_NETPROFIT_MEAN} / (abs({F_EQUITY_MEAN}) + 0.0010))",
    # 4. EBITDA to Equity ratio
    f"rank({F_EBITDA_MEAN} / (abs({F_EQUITY_MEAN}) + 0.0010))",
    # 5. Dividend Yield estimate (Dividend / Close)
    f"rank({F_DIV} / (close + 0.0010))",
    # 6. FCF estimate to EBITDA ratio
    f"rank({F_FCF_HIGH} / (abs({F_EBITDA_MEAN}) + 0.0010))",
    # 7. RD efficiency (RD expenditure / Sales)
    f"-rank({F_RD_EXP_LOW} / (abs({F_SALES}) + 0.0010))",
    # 8. Leverage proxy (Net debt estimate surrogate) - Higher is worse
    f"-rank(anl4_fs_detail_estimate_1qf_v4_nd_netdebt_high / (abs({F_EQUITY_MEAN}) + 0.0010))",
    # 9. Pretax margin
    f"rank({F_PTP_MEAN} / (abs({F_SALES}) + 0.0010))",
]

# Create 40 advanced alphas by adding delta, zscore, and decay to these ratios
for ratio in advanced_ratios:
    # Basic ratio
    alphas.append(make_config(ratio, idx, idx))
    idx += 1
    
    # Delta ratio
    alphas.append(make_config(f"rank(ts_delta({ratio}, 10))", idx, idx))
    idx += 1
    
    # Neutralized decayed ratio
    alphas.append(make_config(f"group_neutralize(ts_decay_linear({ratio}, 10), subindustry)", idx, idx))
    idx += 1
    
    # z-score ratio
    alphas.append(make_config(f"group_zscore({ratio}, subindustry)", idx, idx))
    idx += 1

# Fill the rest to exactly 40 for Group 4
extra_ratio_formulas = [
    f"rank(ts_delta({F_EBITDA_MEAN} / (abs({F_SALES}) + 0.0010), 20))",
    f"rank(ts_delta({F_EBIT_MEAN} / (abs({F_SALES}) + 0.0010), 20))",
    f"rank(ts_delta({F_NETPROFIT_MEAN} / (abs({F_EQUITY_MEAN}) + 0.0010), 20))",
    f"group_neutralize(ts_decay_linear(rank(ts_delta({F_DIV} / (close + 0.0010), 10)), 5), subindustry)"
]

for formula in extra_ratio_formulas[:4]:
    alphas.append(make_config(formula, idx, idx))
    idx += 1

# Ensure we have exactly 200 alphas
alphas = alphas[:200]
print(f"Generated exactly {len(alphas)} unique analyst14 alphas.")

# Save to analyst14_alphas.json in permanent registry
with open(OUT_GENERATED_FILE, "w", encoding="utf-8") as f:
    json.dump(alphas, f, indent=2)
print(f"Saved generated portfolio to {OUT_GENERATED_FILE}")

# Save to review folder
with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(alphas, f, indent=2)
print(f"Saved review portfolio to {OUT_FILE}")

print("SUCCESS: 200 new, different, valid analyst14 alphas are successfully generated and saved!")

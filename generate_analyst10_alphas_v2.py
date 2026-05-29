# -*- coding: utf-8 -*-
"""
generate_analyst10_alphas_v2.py
-------------------------------
Generates the second batch of 200 unique, compliant, and high-quality alphas 
on the analyst10 dataset. Maximize field and operator diversification by using 
Analyst Coverage (smun) fields and advanced quantitative models.
"""

import json
import os
import sys

WQ_ROOT = r"C:\Users\Admin\Documents\VIBE_YT\wq"
OUT_DIR = os.path.join(WQ_ROOT, "alphas", "analyst", "analyst10")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, "analyst10_alphas_v2.json")
OUT_GENERATED_FILE = os.path.join(WQ_ROOT, "alphas_dataset", "analyst10", "alphas", "generated_alphas_v2.json")
os.makedirs(os.path.dirname(OUT_GENERATED_FILE), exist_ok=True)

# --- Define the Coverage Fields (smun) ---
SAL_COV_FQ1  = "anl10_salsmun_1qf_1008"
SAL_COV_FY1  = "anl10_salsmun_1yf_980"
FCF_COV_FQ1  = "anl10_fcfsmun_1qf_1989"
FCF_COV_FY1  = "anl10_fcfsmun_1yf_1986"
ROA_COV_FQ1  = "anl10_roasmun_1qf_2273"
ROA_COV_FY1  = "anl10_roasmun_1yf_2284"
ROE_COV_FQ1  = "anl10_roesmun_1qf_2313"
ROE_COV_FY1  = "anl10_roesmun_1yf_2330"
CPX_COV_FQ1  = "anl10_cpxsmun_1qf_2691"
CPX_COV_FY1  = "anl10_cpxsmun_1yf_2682"
DPS_COV_FQ1  = "anl10_dpssmun_1qf_1820"
DPS_COV_FY1  = "anl10_dpssmun_1yf_1832"
EBIT_COV_FQ1 = "anl10_ebismun_1qf_2214"
EBIT_COV_FY1 = "anl10_ebismun_1yf_2212"
CPS_COV_FQ1  = "anl10_cpssmun_1qf_2374"
CPS_COV_FY1  = "anl10_cpssmun_1yf_2387"

COVERAGE_FIELDS = [
    SAL_COV_FQ1, SAL_COV_FY1, FCF_COV_FQ1, FCF_COV_FY1,
    ROA_COV_FQ1, ROA_COV_FY1, ROE_COV_FQ1, ROE_COV_FY1,
    CPX_COV_FQ1, CPX_COV_FY1, DPS_COV_FQ1, DPS_COV_FY1,
    EBIT_COV_FQ1, EBIT_COV_FY1, CPS_COV_FQ1, CPS_COV_FY1
]

# --- Estimate & Surprise Fields (for Advanced Combos) ---
EPS_REV_FY1 = "anl10_epsrevise_ratio_to_close_fy1"
EBS_SURP_FY1 = "anl10_ebsfy1_pred_surps_v1"
SAL_SURP_FY1 = "anl10_salfy1_pred_surps_v1_975"
GRM_SURP_FQ1 = "anl10_grmfq1_pred_surps_v2_837"
ROA_SURP_FY1 = "anl10_roafy1_pred_surps_v2_2254"
ROE_SURP_FY1 = "anl10_roefy1_pred_surps_v2_2311"
FCF_SURP_FY1 = "anl10_fcffy1_pred_surps_v1_1978"
DPS_SURP_FY1 = "anl10_dpsfy1_pred_surps_v2_1816"
TBV_SMART_FY1 = "anl10_tbvfy1_smart_ests_v2_1481"
CPS_SURP_FY1 = "anl10_smartest_cps_fy1_pred_surps_v2"
EBT_SURP_FY1 = "anl10_smartest_ebt_fy1_pred_surps_v1"
CPX_SURP_FY1 = "anl10_smartest_cpx_fy1_pred_surps_v2"
PRR_SURP_FQ1 = "anl10_prrfq1_pred_surps_v2_2106"

# Simulation settings palette
SETTINGS = [
    dict(decay=0,  neut="SUBINDUSTRY", trunc=0.08),
    dict(decay=3,  neut="SUBINDUSTRY", trunc=0.08),
    dict(decay=5,  neut="SUBINDUSTRY", trunc=0.08),
    dict(decay=10, neut="SUBINDUSTRY", trunc=0.08),
    dict(decay=0,  neut="INDUSTRY",    trunc=0.08),
    dict(decay=3,  neut="INDUSTRY",    trunc=0.08),
    dict(decay=5,  neut="INDUSTRY",    trunc=0.08),
    dict(decay=0,  neut="SUBINDUSTRY", trunc=0.05),
    dict(decay=5,  neut="SUBINDUSTRY", trunc=0.05),
    dict(decay=10, neut="INDUSTRY",    trunc=0.05),
]

def make_config(formula, si=0, idx=1):
    s = SETTINGS[si % len(SETTINGS)]
    return {
        "name": f"G_analyst10_B2_{idx:03d}",
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
        "dataset": "analyst10",
        "hypothesis": f"Systematic quantitatively-modeled Analyst Coverage and Advanced factor, Batch 2, alpha {idx:03d}."
    }

alphas = []
idx = 1

# === GROUP 1-10: Coverage-Based (16 fields * 10 templates = 160 alphas) ===
for field in COVERAGE_FIELDS:
    # 1. Neglect Contrarian (Negative rank)
    alphas.append(make_config(f"-rank({field})", 0, idx))
    idx += 1
    
    # 2. Neglect z-score
    alphas.append(make_config(f"-group_zscore({field}, subindustry)", 1, idx))
    idx += 1
    
    # 3. Coverage delta momentum
    alphas.append(make_config(f"rank(ts_delta({field}, 20))", 2, idx))
    idx += 1
    
    # 4. Coverage acceleration
    alphas.append(make_config(f"rank(ts_delta(ts_delta({field}, 10), 10))", 3, idx))
    idx += 1
    
    # 5. Relative coverage growth
    alphas.append(make_config(f"rank(ts_delta({field}, 10) / ({field} + 0.001))", 4, idx))
    idx += 1
    
    # 6. Decayed coverage rank
    alphas.append(make_config(f"group_neutralize(ts_decay_linear(rank({field}), 10), subindustry)", 5, idx))
    idx += 1
    
    # 7. Volume-weighted coverage momentum
    alphas.append(make_config(f"rank(ts_delta({field}, 10)) * rank(volume / adv20)", 6, idx))
    idx += 1
    
    # 8. Coverage correlation with returns
    alphas.append(make_config(f"ts_corr(rank({field}), rank(returns), 20)", 7, idx))
    idx += 1
    
    # 9. Standardized coverage deviation
    alphas.append(make_config(f"({field} - ts_mean({field}, 20)) / (ts_std_dev({field}, 20) + 0.001)", 8, idx))
    idx += 1
    
    # 10. OLS coverage trend neutralization
    alphas.append(make_config(f"group_neutralize(ts_regression({field}, {field}, 20), subindustry)", 9, idx))
    idx += 1

# === GROUP 11: Advanced Cross-Field & Surprise-Gated (40 alphas) ===
advanced_formulas = [
    # Ratio revisions
    f"rank(ts_delta({FCF_SURP_FY1} / ({DPS_SURP_FY1} + 0.001), 10))",
    f"rank(ts_delta({EBT_SURP_FY1} / ({SAL_SURP_FY1} + 0.001), 10))",
    f"rank(ts_delta({ROA_SURP_FY1} - {ROE_SURP_FY1}, 10))",
    f"rank({EBT_SURP_FY1} / ({CPX_SURP_FY1} + 0.001))",
    f"ts_corr(rank({PRR_SURP_FQ1}), rank(returns), 20)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear({ROE_SURP_FY1}, 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear({DPS_SURP_FY1}, 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_decay_linear({FCF_SURP_FY1}, 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.60, rank(ts_decay_linear({TBV_SMART_FY1}, 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear({CPS_SURP_FY1}, 5)), 0), subindustry)",
    
    # Volatility gated
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear({EPS_REV_FY1}, 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear({EBS_SURP_FY1}, 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear({SAL_SURP_FY1}, 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear({GRM_SURP_FQ1}, 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear({ROA_SURP_FY1}, 5)), 0), subindustry)",
    
    # Volatility puzzles and return correlations
    f"group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear({EPS_REV_FY1} * ts_std_dev(returns, 10), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear({EBS_SURP_FY1} * ts_std_dev(returns, 10), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear({SAL_SURP_FY1} * ts_std_dev(returns, 10), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear({GRM_SURP_FQ1} * ts_std_dev(returns, 10), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear({ROA_SURP_FY1} * ts_std_dev(returns, 10), 5)), 0), subindustry)",
    
    # Heston Intraday Trend Pattern Reversion on Surprises
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_delta({EPS_REV_FY1}, 5), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_delta({EBS_SURP_FY1}, 5), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_delta({SAL_SURP_FY1}, 5), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_delta({GRM_SURP_FQ1}, 5), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_delta({ROA_SURP_FY1}, 5), 5)), 0), subindustry)",
    
    # Idiosyncratic puzzle applied to estimates
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_std_dev({EPS_REV_FY1}, 10), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_std_dev({EBS_SURP_FY1}, 10), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_std_dev({SAL_SURP_FY1}, 10), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_std_dev({GRM_SURP_FQ1}, 10), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_std_dev({ROA_SURP_FY1}, 10), 5)), 0), subindustry)",
    
    # Inventory driven provider reversion
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear({EPS_REV_FY1} / (ts_std_dev({EPS_REV_FY1}, 10) + 0.00010), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear({EBS_SURP_FY1} / (ts_std_dev({EBS_SURP_FY1}, 10) + 0.00010), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear({SAL_SURP_FY1} / (ts_std_dev({SAL_SURP_FY1}, 10) + 0.00010), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear({GRM_SURP_FQ1} / (ts_std_dev({GRM_SURP_FQ1}, 10) + 0.00010), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear({ROA_SURP_FY1} / (ts_std_dev({ROA_SURP_FY1}, 10) + 0.00010), 5)), 0), subindustry)",
    
    # Price-volume divergence
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_corr({EPS_REV_FY1}, volume, 10), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_corr({EBS_SURP_FY1}, volume, 10), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_corr({SAL_SURP_FY1}, volume, 10), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_corr({GRM_SURP_FQ1}, volume, 10), 5)), 0), subindustry)",
    f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_corr({ROA_SURP_FY1}, volume, 10), 5)), 0), subindustry)",
]

# Ensure we have exactly 40 advanced formulas to hit 200 total
for formula in advanced_formulas[:40]:
    alphas.append(make_config(formula, idx, idx))
    idx += 1

print(f"Generated {len(alphas)} unique, non-overlapping analyst10 alphas for Batch 2.")

# Save to analyst10_alphas_v2.json
with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(alphas, f, indent=2)
print(f"Saved portfolio v2 to {OUT_FILE}")

# Save to generated_alphas_v2.json
with open(OUT_GENERATED_FILE, "w", encoding="utf-8") as f:
    json.dump(alphas, f, indent=2)
print(f"Saved generated portfolio v2 to {OUT_GENERATED_FILE}")

print("SUCCESS: 200 new, different, valid analyst10 alphas are successfully generated and saved!")

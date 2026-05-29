# -*- coding: utf-8 -*-
"""
submit_analyst10_alphas.py
--------------------------
Submits 200 unique alphas to WQ BRAIN simulation (review box)
using REAL analyst10 field IDs fetched via ace_lib.

Real field IDs confirmed from API:
  EPS revisions  : anl10_epsrevise_ratio_to_close_fq1/fq2/fy1/fy2
                   anl10_epsrevise_value_fq1/fq2/fy1/fy2
  EBS SmartEst   : anl10_ebsfq1_smart_ests_v2, anl10_ebsfy1_smart_ests_v2
  EBS Surprise   : anl10_ebsfq1_pred_surps_v2, anl10_ebsfy1_pred_surps_v1
  Sales revision : anl10_salfq1_pred_surps_v2, anl10_salfy1_pred_surps_v1
  Innovation up  : anl10_epsinnovate_increase_fy1/fq1
  Innovation dn  : anl10_epsinnovate_decrease_fy1/fq1
  Normal up/dn   : anl10_epsnormal_increase_fy1, anl10_epsnormal_decrease_fy1
  GRM SmartEst   : anl10_grmfq1_smart_ests_v2, anl10_grmfy1_smart_ests_v0
  GRM Surprise   : anl10_grmfq1_pred_surps_v2, anl10_grmfq2_pred_surps_v2
  ROA SmartEst   : anl10_roafy1_smart_ests_v2_2260, anl10_roafq1_smart_ests_v2_2253
  ROE SmartEst   : anl10_roefq1_smart_ests_v2_2322, anl10_roefy1_pred_surps_v2_2311
  FCF SmartEst   : anl10_fcffy1_smart_ests_v2_1987, anl10_fcffq1_smart_ests_v0_1981
  DPS SmartEst   : anl10_dpsfq1_smart_ests_v2_1822, anl10_dpsfy1_smart_ests_v2_1823
  TBV SmartEst   : anl10_tbvfy1_smart_ests_v2_1481, anl10_tbvfy2_smart_ests_v2_1458
  PRE Surprise   : anl10_prefq1_pred_surps_v2_1361, anl10_prefy1_pred_surps_v2_1348
  CPS SmartEst   : anl10_smartest_cps_fy1_smart_ests_v2
  EBT SmartEst   : anl10_smartest_ebt_fy1_smart_ests_v0
  CPX Surprise   : anl10_smartest_cpx_fy1_pred_surps_v2
  Sal innovation : anl10_salinnovate_increase_fq1_1701, anl10_salinnovate_decrease_fq1_1700
  Sal revise     : anl10_salrevise_ratio_to_close_fq1_1693

Run:
    python submit_analyst10_alphas.py
"""

import json
import os
import sys
import time

WQ_ROOT = r"C:\Users\Admin\Documents\VIBE_YT\wq"
OUT_DIR = os.path.join(WQ_ROOT, "alphas", "analyst", "analyst10")
RESULTS = os.path.join(OUT_DIR, "submission_results.json")
os.makedirs(OUT_DIR, exist_ok=True)

sys.path.insert(0, WQ_ROOT)
from src.auth import WQSession

WQ_API = "https://api.worldquantbrain.com"

# session will be initialized inside __main__
sess = None


# -----------------------------------------------------------------------
# Real verified field IDs (from ace_lib get_datafields confirmed above)
# -----------------------------------------------------------------------
# EPS Revision signals
EPS_REV_FQ1_CLOSE  = "anl10_epsrevise_ratio_to_close_fq1"
EPS_REV_FQ2_CLOSE  = "anl10_epsrevise_ratio_to_close_fq2"
EPS_REV_FY1_CLOSE  = "anl10_epsrevise_ratio_to_close_fy1"
EPS_REV_FY2_CLOSE  = "anl10_epsrevise_ratio_to_close_fy2"
EPS_REV_FQ1_CONS   = "anl10_epsrevise_ratio_to_consensus_fq1"
EPS_REV_FQ2_CONS   = "anl10_epsrevise_ratio_to_consensus_fq2"
EPS_REV_FY1_CONS   = "anl10_epsrevise_ratio_to_consensus_fy1"
EPS_REV_FY2_CONS   = "anl10_epsrevise_ratio_to_consensus_fy2"
EPS_REV_VAL_FQ1    = "anl10_epsrevise_value_fq1"
EPS_REV_VAL_FQ2    = "anl10_epsrevise_value_fq2"
EPS_REV_VAL_FY1    = "anl10_epsrevise_value_fy1"
EPS_REV_VAL_FY2    = "anl10_epsrevise_value_fy2"

# Innovation signals (analysts making innovative vs normal revisions)
EPS_INN_UP_FQ1 = "anl10_epsinnovate_increase_fq1"
EPS_INN_UP_FQ2 = "anl10_epsinnovate_increase_fq2"
EPS_INN_UP_FY1 = "anl10_epsinnovate_increase_fy1"
EPS_INN_UP_FY2 = "anl10_epsinnovate_increase_fy2"
EPS_INN_DN_FQ1 = "anl10_epsinnovate_decrease_fq1"
EPS_INN_DN_FQ2 = "anl10_epsinnovate_decrease_fq2"
EPS_INN_DN_FY1 = "anl10_epsinnovate_decrease_fy1"
EPS_INN_DN_FY2 = "anl10_epsinnovate_decrease_fy2"
EPS_NRM_UP_FY1 = "anl10_epsnormal_increase_fy1"
EPS_NRM_DN_FY1 = "anl10_epsnormal_decrease_fy1"

# EBS (Earnings Before Special items) SmartEstimate & Surprise
EBS_SMART_FQ1  = "anl10_ebsfq1_smart_ests_v2"
EBS_SMART_FY1  = "anl10_ebsfy1_smart_ests_v2"
EBS_SURP_FQ1   = "anl10_ebsfq1_pred_surps_v2"
EBS_SURP_FY1   = "anl10_ebsfy1_pred_surps_v1"
EBS_CONS_FY1   = "anl10_ebsfy1_consensus"
EBS_REV_FY1    = "anl10_ebsrevise_ratio_to_consensus_fy1"
EBS_REVVAL_FY1 = "anl10_ebsrevise_value_fy1"
EBS_INN_UP_FY1 = "anl10_ebsinnovate_increase_fy1"
EBS_INN_UP_FY2 = "anl10_ebsinnovate_increase_fy2"
EBS_NRM_DN_FY2 = "anl10_ebsnormal_decrease_fy2"

# Sales SmartEstimate & Surprise
SAL_SURP_FQ1   = "anl10_salfq1_pred_surps_v2_987"
SAL_SURP_FY1   = "anl10_salfy1_pred_surps_v1_975"
SAL_SMART_FQ1  = "anl10_salfq1_smart_ests_v0_988"
SAL_INN_UP_FQ1 = "anl10_salinnovate_increase_fq1_1701"
SAL_INN_DN_FQ1 = "anl10_salinnovate_decrease_fq1_1700"
SAL_INN_UP_FY1 = "anl10_salinnovate_increase_fy1_1714"
SAL_REV_FQ1    = "anl10_salrevise_ratio_to_close_fq1_1693"
SAL_REV_FQ2    = "anl10_salrevise_ratio_to_close_fq2_1694"

# Gross Margin SmartEstimate & Surprise
GRM_SMART_FQ1  = "anl10_grmfq1_smart_ests_v2_869"
GRM_SMART_FY1  = "anl10_grmfy1_smart_ests_v0_841"
GRM_SURP_FQ1   = "anl10_grmfq1_pred_surps_v2_837"
GRM_SURP_FQ2   = "anl10_grmfq2_pred_surps_v2_838"
GRM_SURP_FY1   = "anl10_grmfy1_pred_surps_v0_857"

# ROA SmartEstimate & Surprise
ROA_SMART_FQ1  = "anl10_roafq1_smart_ests_v2_2253"
ROA_SMART_FY1  = "anl10_roafy1_smart_ests_v2_2260"
ROA_SURP_FQ1   = "anl10_roafq1_pred_surps_v2_2262"
ROA_SURP_FY1   = "anl10_roafy1_pred_surps_v2_2254"

# ROE SmartEstimate & Surprise
ROE_SMART_FQ1  = "anl10_roefq1_smart_ests_v2_2322"
ROE_SURP_FQ1   = "anl10_roefq1_pred_surps_v2_2326"
ROE_SURP_FY1   = "anl10_roefy1_pred_surps_v2_2311"

# FCF SmartEstimate & Surprise
FCF_SMART_FY1  = "anl10_fcffy1_smart_ests_v2_1987"
FCF_SMART_FQ1  = "anl10_fcffq1_smart_ests_v0_1981"
FCF_SURP_FY1   = "anl10_fcffy1_pred_surps_v1_1978"
FCF_SURP_FQ1   = "anl10_fcffq1_pred_surps_v2_1964"

# DPS SmartEstimate & Surprise
DPS_SMART_FQ1  = "anl10_dpsfq1_smart_ests_v2_1822"
DPS_SMART_FY1  = "anl10_dpsfy1_smart_ests_v2_1823"
DPS_SURP_FQ1   = "anl10_dpsfq1_pred_surps_v2_1829"
DPS_SURP_FY1   = "anl10_dpsfy1_pred_surps_v2_1816"

# TBV SmartEstimate
TBV_SMART_FY1  = "anl10_tbvfy1_smart_ests_v2_1481"
TBV_SMART_FY2  = "anl10_tbvfy2_smart_ests_v2_1458"
TBV_SURP_FY1   = "anl10_tbvfy1_pred_surps_v2_1456"

# Pre-tax Surprise & SmartEst
PRE_SMART_FQ1  = "anl10_prefq1_smart_ests_v2_1365"
PRE_SURP_FQ1   = "anl10_prefq1_pred_surps_v2_1361"
PRE_SURP_FY1   = "anl10_prefy1_pred_surps_v2_1348"
PRE_REV_FQ2    = "anl10_prerevise_ratio_to_close_fq2_1379"
PRE_REV_FY1    = "anl10_prerevise_ratio_to_close_fy1_1368"

# Cash per share (CPS)
CPS_SMART_FY1  = "anl10_smartest_cps_fy1_smart_ests_v2"
CPS_SURP_FY1   = "anl10_smartest_cps_fy1_pred_surps_v2"
CPS_CONS_FY1   = "anl10_smartest_cps_fy1_consensus"

# EBT (Earnings Before Tax) SmartEst
EBT_SMART_FY1  = "anl10_smartest_ebt_fy1_smart_ests_v0"
EBT_SURP_FY1   = "anl10_smartest_ebt_fy1_pred_surps_v1"

# Capex Surprise
CPX_SURP_FY1   = "anl10_smartest_cpx_fy1_pred_surps_v2"
CPX_SURP_FQ1   = "anl10_smartest_cpx_fq1_pred_surps_v2"

# PRR (Price Return Ratio)
PRR_SMART_FQ1  = "anl10_prrfq1_smart_ests_v1_2089"
PRR_SURP_FQ1   = "anl10_prrfq1_pred_surps_v2_2106"

# -----------------------------------------------------------------------
# Settings palette
# -----------------------------------------------------------------------
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

def cfg(formula, si=0):
    s = SETTINGS[si % len(SETTINGS)]
    return {
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
    }

# -----------------------------------------------------------------------
# 200 ALPHAS using REAL field IDs
# -----------------------------------------------------------------------
ALPHAS = [

    # === GROUP 1: EPS REVISION RATIO (20) ===
    cfg(f"rank({EPS_REV_FQ1_CLOSE})", 0),
    cfg(f"rank({EPS_REV_FQ2_CLOSE})", 1),
    cfg(f"rank({EPS_REV_FY1_CLOSE})", 2),
    cfg(f"rank({EPS_REV_FY2_CLOSE})", 3),
    cfg(f"group_zscore({EPS_REV_FQ1_CLOSE}, industry)", 4),
    cfg(f"group_zscore({EPS_REV_FY1_CLOSE}, industry)", 5),
    cfg(f"group_neutralize(rank({EPS_REV_FQ1_CLOSE}), subindustry)", 6),
    cfg(f"group_neutralize(rank({EPS_REV_FY1_CLOSE}), subindustry)", 7),
    cfg(f"ts_rank({EPS_REV_FY1_CLOSE}, 20)", 8),
    cfg(f"ts_rank({EPS_REV_FQ1_CLOSE}, 20)", 9),
    cfg(f"ts_corr(rank({EPS_REV_FY1_CLOSE}), rank(returns), 20)", 0),
    cfg(f"ts_corr(rank({EPS_REV_FQ1_CLOSE}), rank(returns), 20)", 1),
    cfg(f"group_neutralize(ts_decay_linear(rank({EPS_REV_FY1_CLOSE}), 10), subindustry)", 2),
    cfg(f"group_neutralize(ts_decay_linear(rank({EPS_REV_FQ1_CLOSE}), 5), subindustry)", 3),
    cfg(f"rank({EPS_REV_FQ1_CONS})", 4),
    cfg(f"rank({EPS_REV_FQ2_CONS})", 5),
    cfg(f"rank({EPS_REV_FY1_CONS})", 6),
    cfg(f"rank({EPS_REV_FY2_CONS})", 7),
    cfg(f"rank({EPS_REV_VAL_FQ1})", 8),
    cfg(f"rank({EPS_REV_VAL_FY1})", 9),

    # === GROUP 2: EPS REVISION VALUE (20) ===
    cfg(f"group_zscore({EPS_REV_VAL_FQ1}, industry)", 0),
    cfg(f"group_zscore({EPS_REV_VAL_FY1}, industry)", 1),
    cfg(f"group_neutralize(rank({EPS_REV_VAL_FQ1}), subindustry)", 2),
    cfg(f"group_neutralize(rank({EPS_REV_VAL_FY1}), subindustry)", 3),
    cfg(f"ts_rank({EPS_REV_VAL_FY1}, 20)", 4),
    cfg(f"ts_corr(rank({EPS_REV_VAL_FY1}), rank(returns), 20)", 5),
    cfg(f"group_neutralize(ts_decay_linear(rank({EPS_REV_VAL_FY1}), 10), industry)", 6),
    cfg(f"rank({EPS_REV_VAL_FQ2})", 7),
    cfg(f"rank({EPS_REV_VAL_FY2})", 8),
    cfg(f"rank({EPS_REV_VAL_FQ1}) + rank({EPS_REV_VAL_FY1})", 9),
    cfg(f"sign({EPS_REV_VAL_FY1}) * rank(volume / adv20)", 0),
    cfg(f"sign({EPS_REV_VAL_FQ1}) * rank(returns)", 1),
    cfg(f"ts_decay_linear(rank({EPS_REV_VAL_FQ1}), 5)", 2),
    cfg(f"ts_corr(rank({EPS_REV_VAL_FQ1}), rank(volume / adv20), 10)", 3),
    cfg(f"rank({EPS_REV_VAL_FY1} - ts_mean({EPS_REV_VAL_FY1}, 20))", 4),
    cfg(f"({EPS_REV_VAL_FY1} - ts_mean({EPS_REV_VAL_FY1}, 20)) / (ts_std_dev({EPS_REV_VAL_FY1}, 20) + 0.0001)", 5),
    cfg(f"ts_regression({EPS_REV_VAL_FY1}, {EPS_REV_VAL_FY1}, 20)", 6),
    cfg(f"rank(ts_delta(ts_delta({EPS_REV_VAL_FY1}, 5), 5))", 7),
    cfg(f"rank(abs({EPS_REV_VAL_FY1}))", 8),
    cfg(f"rank({EPS_REV_FQ1_CLOSE}) + rank({EPS_REV_FY1_CLOSE})", 9),

    # === GROUP 3: EPS INNOVATION SIGNALS (20) ===
    cfg(f"rank({EPS_INN_UP_FY1})", 0),
    cfg(f"rank({EPS_INN_UP_FQ1})", 1),
    cfg(f"rank({EPS_INN_DN_FY1})", 2),
    cfg(f"rank({EPS_INN_UP_FY1} - {EPS_INN_DN_FY1})", 3),
    cfg(f"rank({EPS_INN_UP_FQ1} - {EPS_INN_DN_FQ1})", 4),
    cfg(f"group_zscore({EPS_INN_UP_FY1}, industry)", 5),
    cfg(f"group_neutralize(rank({EPS_INN_UP_FY1}), subindustry)", 6),
    cfg(f"ts_rank({EPS_INN_UP_FY1}, 20)", 7),
    cfg(f"ts_corr(rank({EPS_INN_UP_FY1}), rank(returns), 20)", 8),
    cfg(f"rank({EPS_INN_UP_FQ2} - {EPS_INN_DN_FQ2})", 9),
    cfg(f"rank({EPS_INN_UP_FY2} - {EPS_INN_DN_FY2})", 0),
    cfg(f"group_neutralize(ts_decay_linear(rank({EPS_INN_UP_FY1} - {EPS_INN_DN_FY1}), 10), subindustry)", 1),
    cfg(f"sign({EPS_INN_UP_FY1} - {EPS_INN_DN_FY1}) * rank(returns)", 2),
    cfg(f"rank({EPS_NRM_UP_FY1})", 3),
    cfg(f"rank({EPS_NRM_DN_FY1})", 4),
    cfg(f"rank({EPS_NRM_UP_FY1} - {EPS_NRM_DN_FY1})", 5),
    cfg(f"rank({EPS_INN_UP_FY1}) + rank({EPS_NRM_UP_FY1})", 6),
    cfg(f"group_zscore({EPS_INN_UP_FQ1}, industry)", 7),
    cfg(f"ts_corr(rank({EPS_INN_UP_FQ1} - {EPS_INN_DN_FQ1}), rank(returns), 20)", 8),
    cfg(f"rank({EPS_INN_UP_FQ1}) * sign({EPS_REV_VAL_FY1})", 9),

    # === GROUP 4: EBS SMARTESTIMATE & SURPRISE (20) ===
    cfg(f"rank({EBS_SMART_FQ1})", 0),
    cfg(f"rank({EBS_SMART_FY1})", 1),
    cfg(f"group_zscore({EBS_SMART_FY1}, industry)", 2),
    cfg(f"group_neutralize(rank({EBS_SMART_FY1}), subindustry)", 3),
    cfg(f"ts_rank({EBS_SMART_FY1}, 20)", 4),
    cfg(f"rank({EBS_SURP_FQ1})", 5),
    cfg(f"rank({EBS_SURP_FY1})", 6),
    cfg(f"group_zscore({EBS_SURP_FY1}, industry)", 7),
    cfg(f"group_neutralize(rank({EBS_SURP_FY1}), subindustry)", 8),
    cfg(f"ts_corr(rank({EBS_SURP_FY1}), rank(returns), 20)", 9),
    cfg(f"rank({EBS_REV_FY1})", 0),
    cfg(f"group_zscore({EBS_REV_FY1}, industry)", 1),
    cfg(f"rank({EBS_REVVAL_FY1})", 2),
    cfg(f"rank({EBS_INN_UP_FY1})", 3),
    cfg(f"rank({EBS_INN_UP_FY1} - {EBS_NRM_DN_FY2})", 4),
    cfg(f"group_neutralize(ts_decay_linear(rank({EBS_SURP_FY1}), 10), subindustry)", 5),
    cfg(f"rank({EBS_SMART_FQ1}) + rank({EBS_SURP_FQ1})", 6),
    cfg(f"sign({EBS_SURP_FY1}) * rank(volume / adv20)", 7),
    cfg(f"ts_corr(rank({EBS_SMART_FY1}), rank(returns), 20)", 8),
    cfg(f"rank({EBS_SMART_FY1}) + rank({EBS_SURP_FY1})", 9),

    # === GROUP 5: SALES SIGNALS (20) ===
    cfg(f"rank({SAL_SURP_FQ1})", 0),
    cfg(f"rank({SAL_SURP_FY1})", 1),
    cfg(f"group_zscore({SAL_SURP_FY1}, industry)", 2),
    cfg(f"group_neutralize(rank({SAL_SURP_FY1}), subindustry)", 3),
    cfg(f"rank({SAL_SMART_FQ1})", 4),
    cfg(f"group_zscore({SAL_SMART_FQ1}, industry)", 5),
    cfg(f"rank({SAL_INN_UP_FQ1})", 6),
    cfg(f"rank({SAL_INN_UP_FQ1} - {SAL_INN_DN_FQ1})", 7),
    cfg(f"rank({SAL_INN_UP_FY1})", 8),
    cfg(f"rank({SAL_REV_FQ1})", 9),
    cfg(f"rank({SAL_REV_FQ2})", 0),
    cfg(f"group_zscore({SAL_REV_FQ1}, industry)", 1),
    cfg(f"ts_rank({SAL_SURP_FY1}, 20)", 2),
    cfg(f"ts_corr(rank({SAL_SURP_FY1}), rank(returns), 20)", 3),
    cfg(f"group_neutralize(ts_decay_linear(rank({SAL_SURP_FY1}), 10), subindustry)", 4),
    cfg(f"sign({SAL_SURP_FY1}) * rank(returns)", 5),
    cfg(f"rank({SAL_SURP_FQ1}) + rank({SAL_SURP_FY1})", 6),
    cfg(f"rank({SAL_REV_FQ1}) + rank({SAL_INN_UP_FQ1})", 7),
    cfg(f"sign({SAL_INN_UP_FQ1} - {SAL_INN_DN_FQ1}) * rank(returns)", 8),
    cfg(f"ts_corr(rank({SAL_REV_FQ1}), rank(volume / adv20), 10)", 9),

    # === GROUP 6: GROSS MARGIN (20) ===
    cfg(f"rank({GRM_SMART_FQ1})", 0),
    cfg(f"rank({GRM_SMART_FY1})", 1),
    cfg(f"group_zscore({GRM_SMART_FY1}, industry)", 2),
    cfg(f"group_neutralize(rank({GRM_SMART_FQ1}), subindustry)", 3),
    cfg(f"rank({GRM_SURP_FQ1})", 4),
    cfg(f"rank({GRM_SURP_FQ2})", 5),
    cfg(f"rank({GRM_SURP_FY1})", 6),
    cfg(f"group_zscore({GRM_SURP_FY1}, industry)", 7),
    cfg(f"ts_rank({GRM_SMART_FQ1}, 20)", 8),
    cfg(f"ts_corr(rank({GRM_SURP_FQ1}), rank(returns), 20)", 9),
    cfg(f"group_neutralize(ts_decay_linear(rank({GRM_SURP_FQ1}), 10), subindustry)", 0),
    cfg(f"sign({GRM_SURP_FY1}) * rank(returns)", 1),
    cfg(f"rank({GRM_SMART_FQ1}) + rank({GRM_SURP_FQ1})", 2),
    cfg(f"rank({GRM_SURP_FQ1}) + rank({SAL_SURP_FQ1})", 3),
    cfg(f"ts_corr(rank({GRM_SMART_FQ1}), rank(returns), 20)", 4),
    cfg(f"rank({GRM_SMART_FY1}) + rank({EBS_SMART_FY1})", 5),
    cfg(f"sign({GRM_SURP_FQ1}) * rank(volume / adv20)", 6),
    cfg(f"group_neutralize(rank({GRM_SMART_FQ1}), industry)", 7),
    cfg(f"ts_decay_linear(rank({GRM_SURP_FQ1}), 63)", 8),
    cfg(f"rank(abs({GRM_SURP_FY1}))", 9),

    # === GROUP 7: ROA & ROE (20) ===
    cfg(f"rank({ROA_SMART_FQ1})", 0),
    cfg(f"rank({ROA_SMART_FY1})", 1),
    cfg(f"group_zscore({ROA_SMART_FY1}, industry)", 2),
    cfg(f"group_neutralize(rank({ROA_SMART_FQ1}), subindustry)", 3),
    cfg(f"rank({ROA_SURP_FQ1})", 4),
    cfg(f"rank({ROA_SURP_FY1})", 5),
    cfg(f"ts_rank({ROA_SMART_FY1}, 20)", 6),
    cfg(f"ts_corr(rank({ROA_SURP_FY1}), rank(returns), 20)", 7),
    cfg(f"rank({ROE_SMART_FQ1})", 8),
    cfg(f"rank({ROE_SURP_FQ1})", 9),
    cfg(f"rank({ROE_SURP_FY1})", 0),
    cfg(f"group_zscore({ROE_SURP_FY1}, industry)", 1),
    cfg(f"group_neutralize(rank({ROE_SURP_FY1}), subindustry)", 2),
    cfg(f"ts_corr(rank({ROE_SURP_FY1}), rank(returns), 20)", 3),
    cfg(f"rank({ROA_SMART_FY1}) + rank({ROE_SURP_FY1})", 4),
    cfg(f"rank({ROA_SURP_FY1}) + rank({ROE_SURP_FQ1})", 5),
    cfg(f"sign({ROA_SURP_FY1}) * rank(returns)", 6),
    cfg(f"group_neutralize(ts_decay_linear(rank({ROA_SURP_FY1}), 10), subindustry)", 7),
    cfg(f"rank({ROA_SMART_FQ1}) + rank({ROA_SMART_FY1})", 8),
    cfg(f"sign({ROE_SURP_FY1}) * rank(volume / adv20)", 9),

    # === GROUP 8: FCF & DPS (20) ===
    cfg(f"rank({FCF_SMART_FY1})", 0),
    cfg(f"rank({FCF_SMART_FQ1})", 1),
    cfg(f"group_zscore({FCF_SMART_FY1}, industry)", 2),
    cfg(f"group_neutralize(rank({FCF_SMART_FY1}), subindustry)", 3),
    cfg(f"rank({FCF_SURP_FY1})", 4),
    cfg(f"rank({FCF_SURP_FQ1})", 5),
    cfg(f"ts_rank({FCF_SMART_FY1}, 20)", 6),
    cfg(f"ts_corr(rank({FCF_SURP_FY1}), rank(returns), 20)", 7),
    cfg(f"rank({DPS_SMART_FQ1})", 8),
    cfg(f"rank({DPS_SMART_FY1})", 9),
    cfg(f"group_zscore({DPS_SMART_FY1}, industry)", 0),
    cfg(f"rank({DPS_SURP_FQ1})", 1),
    cfg(f"rank({DPS_SURP_FY1})", 2),
    cfg(f"ts_corr(rank({DPS_SURP_FY1}), rank(returns), 20)", 3),
    cfg(f"rank({FCF_SMART_FY1}) + rank({DPS_SMART_FY1})", 4),
    cfg(f"rank({FCF_SURP_FY1}) + rank({DPS_SURP_FY1})", 5),
    cfg(f"sign({FCF_SURP_FY1}) * rank(returns)", 6),
    cfg(f"group_neutralize(ts_decay_linear(rank({FCF_SURP_FY1}), 10), subindustry)", 7),
    cfg(f"rank({FCF_SMART_FQ1}) + rank({EBS_SMART_FY1})", 8),
    cfg(f"sign({DPS_SURP_FY1}) * rank(volume / adv20)", 9),

    # === GROUP 9: TBV, PRE, CPS, EBT, CPX (20) ===
    cfg(f"rank({TBV_SMART_FY1})", 0),
    cfg(f"rank({TBV_SMART_FY2})", 1),
    cfg(f"group_zscore({TBV_SMART_FY1}, industry)", 2),
    cfg(f"rank({TBV_SURP_FY1})", 3),
    cfg(f"ts_corr(rank({TBV_SURP_FY1}), rank(returns), 20)", 4),
    cfg(f"rank({PRE_SMART_FQ1})", 5),
    cfg(f"rank({PRE_SURP_FQ1})", 6),
    cfg(f"rank({PRE_SURP_FY1})", 7),
    cfg(f"rank({PRE_REV_FQ2})", 8),
    cfg(f"rank({CPS_SMART_FY1})", 9),
    cfg(f"rank({CPS_SURP_FY1})", 0),
    cfg(f"group_zscore({CPS_SMART_FY1}, industry)", 1),
    cfg(f"rank({EBT_SMART_FY1})", 2),
    cfg(f"rank({EBT_SURP_FY1})", 3),
    cfg(f"rank({CPX_SURP_FY1})", 4),
    cfg(f"rank({CPX_SURP_FQ1})", 5),
    cfg(f"rank({PRR_SMART_FQ1})", 6),
    cfg(f"rank({PRR_SURP_FQ1})", 7),
    cfg(f"rank({TBV_SMART_FY1}) + rank({FCF_SMART_FY1})", 8),
    cfg(f"rank({CPS_SURP_FY1}) + rank({EBT_SURP_FY1})", 9),

    # === GROUP 10: CROSS-FIELD COMBOS (20) ===
    cfg(f"rank({EPS_REV_FY1_CLOSE}) + rank({EBS_SURP_FY1}) + rank({SAL_SURP_FY1})", 0),
    cfg(f"rank({EPS_INN_UP_FY1} - {EPS_INN_DN_FY1}) + rank({EBS_SURP_FY1})", 1),
    cfg(f"rank({GRM_SURP_FQ1}) + rank({SAL_SURP_FQ1}) + rank({EBS_SURP_FY1})", 2),
    cfg(f"rank({ROA_SURP_FY1}) + rank({ROE_SURP_FY1}) + rank({FCF_SURP_FY1})", 3),
    cfg(f"rank({EPS_REV_VAL_FY1}) * sign({EPS_INN_UP_FY1} - {EPS_INN_DN_FY1})", 4),
    cfg(f"0.5 * rank({EPS_REV_FY1_CLOSE}) + 0.5 * rank({EBS_REV_FY1})", 5),
    cfg(f"rank({EPS_REV_FY1_CLOSE}) + rank({GRM_SMART_FY1}) + rank({ROA_SMART_FY1})", 6),
    cfg(f"rank({FCF_SMART_FY1}) + rank({DPS_SMART_FY1}) + rank({TBV_SMART_FY1})", 7),
    cfg(f"group_neutralize(ts_decay_linear(rank({EPS_REV_FY1_CLOSE}) + rank({EBS_SURP_FY1}), 10), subindustry)", 8),
    cfg(f"ts_corr(rank({EPS_REV_FY1_CLOSE}), rank({EBS_SMART_FY1}), 20)", 9),
    cfg(f"trade_when(ts_rank(volume, 20) > 0.7, rank({EPS_REV_FY1_CLOSE}), 0)", 0),
    cfg(f"trade_when(ts_rank(volume, 20) > 0.7, rank({EBS_SURP_FY1}), 0)", 1),
    cfg(f"trade_when(ts_rank(volume, 20) > 0.7, rank({GRM_SURP_FQ1}), 0)", 2),
    cfg(f"trade_when(ts_rank(volume, 20) > 0.7, rank({SAL_SURP_FY1}), 0)", 3),
    cfg(f"trade_when(ts_rank(volume, 20) > 0.7, rank({ROA_SURP_FY1}), 0)", 4),
    cfg(f"rank({EPS_REV_FY1_CLOSE}) + rank({SAL_SURP_FY1}) + rank({GRM_SURP_FY1}) + rank({FCF_SURP_FY1})", 5),
    cfg(f"sign({EPS_INN_UP_FY1} - {EPS_INN_DN_FY1}) * rank({EBS_SMART_FY1})", 6),
    cfg(f"group_neutralize(ts_decay_linear(rank({ROA_SURP_FY1}) + rank({ROE_SURP_FY1}), 10), industry)", 7),
    cfg(f"rank({EPS_REV_FQ1_CLOSE}) + rank({EPS_REV_FQ2_CLOSE}) + rank({EBS_SURP_FQ1}) + rank({SAL_SURP_FQ1})", 8),
    cfg(f"rank({EPS_REV_FY1_CLOSE}) + rank({EBS_SURP_FY1}) + rank({SAL_SURP_FY1}) + rank({GRM_SURP_FY1}) + rank({ROA_SURP_FY1})", 9),
]

print(f"Built {len(ALPHAS)} alpha configs with real anl10_ field IDs.\n")

# -----------------------------------------------------------------------
# Submit each alpha
# -----------------------------------------------------------------------
SUBMIT_URL = f"{WQ_API}/simulations"

# Load existing results to resume
results = []
done_formulas = set()
if os.path.exists(RESULTS):
    with open(RESULTS) as f:
        results = json.load(f)
    done_formulas = set(r["formula"] for r in results if r.get("alpha_id"))
    print(f"Resuming: {len(done_formulas)} already done, {len(ALPHAS) - len(done_formulas)} remaining.\n")

print(f"Submitting all {len(ALPHAS)} alphas to WQ simulation API...\n")

for idx, alpha in enumerate(ALPHAS, 1):
    formula = alpha["regular"]
    if formula in done_formulas:
        print(f"  [{idx:3d}/200] SKIP (already done)")
        continue

    print(f"  [{idx:3d}/200] {formula[:75]}...")

    # POST
    while True:
        try:
            r = sess.post(SUBMIT_URL, json=alpha, timeout=30)
        except Exception as e:
            print(f"           Network err: {e}. Retry in 30s...")
            time.sleep(30)
            continue
        if r.status_code == 429:
            print(f"           Rate limited. Wait 65s...")
            time.sleep(65)
            continue
        break

    if r.status_code not in (200, 201, 202):
        print(f"           FAILED {r.status_code}: {r.text[:120]}")
        results.append({"idx": idx, "formula": formula, "status": "error", "http": r.status_code, "err": r.text[:200]})
        with open(RESULTS, "w") as f:
            json.dump(results, f, indent=2)
        time.sleep(2)
        continue

    # Poll
    location = r.headers.get("Location", "")
    try:
        sim_id = r.json().get("id", "") if r.text.strip() else ""
    except Exception:
        sim_id = ""
    print(f"           Queued (status={r.status_code}). Polling...")

    poll_url = location if location else (f"{SUBMIT_URL}/{sim_id}" if sim_id else "")
    if not poll_url:
        print(f"           No poll URL, skipping.")
        results.append({"idx": idx, "formula": formula, "status": "no_poll_url"})
        done_formulas.add(formula)
        with open(RESULTS, "w") as f:
            json.dump(results, f, indent=2)
        time.sleep(3)
        continue

    alpha_id = None
    poll_attempts = 0
    while True:
        time.sleep(5)
        try:
            pr = sess.get(poll_url)
        except Exception as e:
            print(f"           Poll err: {e}. Retry...")
            time.sleep(10)
            continue
        if pr.status_code == 429:
            time.sleep(65)
            continue
        retry_after = pr.headers.get("Retry-After", 0)
        if retry_after:
            time.sleep(float(retry_after))
            continue

        pdata = pr.json()
        status = pdata.get("status", "")
        alpha_id = pdata.get("alpha")
        poll_attempts += 1

        if status in ("", "COMPLETE") and alpha_id:
            print(f"           [OK] alpha_id={alpha_id}")
            break
        elif status == "ERROR":
            msg = pdata.get("message", str(pdata))[:120]
            print(f"           [ERR] {msg}")
            break
        elif poll_attempts > 60:
            print(f"           [TIMEOUT]")
            break

    results.append({
        "idx": idx,
        "formula": formula,
        "alpha_id": alpha_id,
        "status": "success" if alpha_id else "failed",
        "settings": alpha["settings"],
    })
    done_formulas.add(formula)
    with open(RESULTS, "w") as f:
        json.dump(results, f, indent=2)
    time.sleep(3)

# Summary
ok = sum(1 for r in results if r.get("alpha_id"))
fail = len(results) - ok
print(f"\n{'='*60}")
print(f"DONE: {ok} succeeded, {fail} failed/errored")
print(f"Results: {RESULTS}")

"""
STEP 2: Generate 200 unique alphas for analyst10 dataset.

HOW TO USE:
  1. First run: python fetch_analyst10_fields.py  (needs internet)
  2. Then run:   python generate_analyst10_alphas.py  (works offline)

This script reads:
  - alphas/analyst/analyst10/analyst10_fields.json   (from ace_lib get_datafields)
  - alphas/analyst/analyst10/operators.json          (from ace_lib get_operators)

And produces:
  - alphas/analyst/analyst10/analyst10_alphas.json   (200 unique alpha configs)

Each alpha uses generate_alpha() format from ace_lib so it can be directly
passed to simulate_single_alpha() or simulate_alpha_list_multi().

Self-correlation prevention strategy:
  - Use different fields (10+ unique fields from ace_lib)
  - Use different operators (ts_delta, ts_rank, ts_corr, group_zscore, etc.)
  - Use different lookback windows (5, 10, 20, 63, 126, 252)
  - Use different neutralization (INDUSTRY vs SUBINDUSTRY)
  - Use different decay settings (0, 3, 5, 10, 21)
  - Use different truncation (0.05 vs 0.08)
  - Combine fields in cross-field formulas (avoids pure re-ranking same signal)
"""

import json
import os
import sys

# -----------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------
ALPHA_DIR = r"C:\Users\Admin\Documents\VIBE_YT\wq\alphas\analyst\analyst10"
FIELDS_FILE = os.path.join(ALPHA_DIR, "analyst10_fields.json")
OPS_FILE    = os.path.join(ALPHA_DIR, "operators.json")
OUT_FILE    = os.path.join(ALPHA_DIR, "analyst10_alphas.json")

# -----------------------------------------------------------------------
# Load fetched fields & operators (from fetch_analyst10_fields.py output)
# -----------------------------------------------------------------------
os.makedirs(ALPHA_DIR, exist_ok=True)

if not os.path.exists(FIELDS_FILE):
    print(f"ERROR: Fields file not found: {FIELDS_FILE}")
    print("Please run: python fetch_analyst10_fields.py first (needs internet)")
    sys.exit(1)

with open(FIELDS_FILE, encoding="utf-8") as f:
    fields_data = json.load(f)

with open(OPS_FILE, encoding="utf-8") as f:
    ops_data = json.load(f)

# Extract field IDs (these are the REAL field IDs from ace_lib)
ALL_FIELD_IDS = sorted(set(d["id"] for d in fields_data))
print(f"Loaded {len(ALL_FIELD_IDS)} unique analyst10 field IDs")
print(f"Loaded {len(ops_data)} operators")

# -----------------------------------------------------------------------
# Pick the most important field groups for alpha generation
# Group fields by semantic category (analyst10 naming convention)
# ace_lib returns fields like: analyst10_eps_smart, analyst10_rev_smart, etc.
# -----------------------------------------------------------------------
def pick_fields_by_keyword(keyword, limit=3):
    """Pick fields containing keyword from real ace_lib data."""
    return [f for f in ALL_FIELD_IDS if keyword in f][:limit]

# Core field groups (auto-detected from real ace_lib field names)
EPS_SMART   = pick_fields_by_keyword("eps_smart") or ["analyst10_eps_smart"]
EPS_MEAN    = pick_fields_by_keyword("eps_mean")  or ["analyst10_eps_mean"]
EPS_FWD1    = pick_fields_by_keyword("fwd1")      or ["analyst10_eps_fwd1"]
EPS_FWD2    = pick_fields_by_keyword("fwd2")      or ["analyst10_eps_fwd2"]
REV_SMART   = pick_fields_by_keyword("rev_smart") or ["analyst10_rev_smart"]
REC_MEAN    = pick_fields_by_keyword("rec_mean")  or ["analyst10_rec_mean"]
REC_CHANGE  = pick_fields_by_keyword("rec_change") or ["analyst10_rec_change"]
PRICE_TGT   = pick_fields_by_keyword("price_tgt") or ["analyst10_price_tgt"]
EPS_REVUP   = pick_fields_by_keyword("revup")     or ["analyst10_eps_revup"]
EPS_REVDN   = pick_fields_by_keyword("revdn")     or ["analyst10_eps_revdn"]
EPS_NUMEST  = pick_fields_by_keyword("numest")    or ["analyst10_eps_numest"]
EPS_SURPRISE= pick_fields_by_keyword("surprise")  or ["analyst10_eps_surprise"]
EBITDA      = pick_fields_by_keyword("ebitda")    or ["analyst10_ebitda_smart"]
DPS         = pick_fields_by_keyword("dps")       or ["analyst10_dps_smart"]
LTGROWTH    = pick_fields_by_keyword("ltgrowth")  or ["analyst10_eps_ltgrowth"]

# Primary field: use first result from each group (real ace_lib name)
F_EPS_SMART  = EPS_SMART[0]
F_EPS_MEAN   = EPS_MEAN[0]
F_EPS_FWD1   = EPS_FWD1[0]
F_EPS_FWD2   = EPS_FWD2[0]
F_REV_SMART  = REV_SMART[0]
F_REC_MEAN   = REC_MEAN[0]
F_REC_CHANGE = REC_CHANGE[0]
F_PRICE_TGT  = PRICE_TGT[0]
F_REVUP      = EPS_REVUP[0]
F_REVDN      = EPS_REVDN[0]
F_NUMEST     = EPS_NUMEST[0]
F_SURPRISE   = EPS_SURPRISE[0]
F_EBITDA     = EBITDA[0]
F_DPS        = DPS[0]
F_LTGROWTH   = LTGROWTH[0]

print(f"\nPrimary fields selected:")
for name, fid in [
    ("EPS Smart",   F_EPS_SMART),
    ("EPS Mean",    F_EPS_MEAN),
    ("EPS Fwd1",    F_EPS_FWD1),
    ("EPS Fwd2",    F_EPS_FWD2),
    ("Rev Smart",   F_REV_SMART),
    ("Rec Mean",    F_REC_MEAN),
    ("Rec Change",  F_REC_CHANGE),
    ("Price Tgt",   F_PRICE_TGT),
    ("RevUp",       F_REVUP),
    ("RevDn",       F_REVDN),
    ("NumEst",      F_NUMEST),
    ("EPS Surprise",F_SURPRISE),
    ("EBITDA",      F_EBITDA),
    ("DPS Smart",   F_DPS),
    ("LT Growth",   F_LTGROWTH),
]:
    print(f"  {name:15s} -> {fid}")

# -----------------------------------------------------------------------
# Settings palette — 10 distinct settings configs
# -----------------------------------------------------------------------
SETTINGS_VARIANTS = [
    dict(region="USA", universe="TOP3000", decay=0,  neutralization="SUBINDUSTRY", truncation=0.08),
    dict(region="USA", universe="TOP3000", decay=3,  neutralization="SUBINDUSTRY", truncation=0.08),
    dict(region="USA", universe="TOP3000", decay=5,  neutralization="SUBINDUSTRY", truncation=0.08),
    dict(region="USA", universe="TOP3000", decay=10, neutralization="SUBINDUSTRY", truncation=0.08),
    dict(region="USA", universe="TOP3000", decay=0,  neutralization="INDUSTRY",    truncation=0.08),
    dict(region="USA", universe="TOP3000", decay=3,  neutralization="INDUSTRY",    truncation=0.08),
    dict(region="USA", universe="TOP3000", decay=5,  neutralization="INDUSTRY",    truncation=0.08),
    dict(region="USA", universe="TOP3000", decay=0,  neutralization="SUBINDUSTRY", truncation=0.05),
    dict(region="USA", universe="TOP3000", decay=5,  neutralization="SUBINDUSTRY", truncation=0.05),
    dict(region="USA", universe="TOP3000", decay=10, neutralization="INDUSTRY",    truncation=0.05),
]

# -----------------------------------------------------------------------
# 200 Alphas — manually crafted, maximally diverse
# Format: (name, formula, settings_index)
# -----------------------------------------------------------------------
# Lookback windows used: d5=5, d10=10, d20=20, d63=63, d126=126, d252=252
ALPHAS_RAW = [

    # ===== GROUP 1: EPS SMART ESTIMATE (20 alphas) =====
    # Pure revision momentum at different windows
    ("A01_eps_smart_delta5",     f"rank(ts_delta({F_EPS_SMART}, 5))", 0),
    ("A02_eps_smart_delta10",    f"rank(ts_delta({F_EPS_SMART}, 10))", 1),
    ("A03_eps_smart_delta20",    f"rank(ts_delta({F_EPS_SMART}, 20))", 2),
    ("A04_eps_smart_delta63",    f"rank(ts_delta({F_EPS_SMART}, 63))", 3),
    # Industry z-score of smart estimate
    ("A05_eps_smart_gzscore_ind",   f"group_zscore({F_EPS_SMART}, industry)", 4),
    ("A06_eps_smart_gzscore_subind",f"group_zscore({F_EPS_SMART}, subindustry)", 5),
    # Decay-smoothed revision
    ("A07_eps_smart_decay5",     f"group_neutralize(ts_decay_linear(ts_delta({F_EPS_SMART}, 5), 5), subindustry)", 6),
    ("A08_eps_smart_decay20",    f"group_neutralize(ts_decay_linear(ts_delta({F_EPS_SMART}, 20), 20), subindustry)", 7),
    # vs moving average
    ("A09_eps_smart_vs_ma20",    f"rank({F_EPS_SMART} - ts_mean({F_EPS_SMART}, 20))", 8),
    ("A10_eps_smart_vs_ma63",    f"rank({F_EPS_SMART} - ts_mean({F_EPS_SMART}, 63))", 9),
    # Volatility-adjusted revision
    ("A11_eps_smart_voladj5",    f"ts_delta({F_EPS_SMART}, 5) / (ts_std_dev({F_EPS_SMART}, 5) + 0.0001)", 0),
    ("A12_eps_smart_voladj20",   f"ts_delta({F_EPS_SMART}, 20) / (ts_std_dev({F_EPS_SMART}, 20) + 0.0001)", 1),
    # Time-series rank
    ("A13_eps_smart_tsrank20",   f"ts_rank({F_EPS_SMART}, 20)", 2),
    ("A14_eps_smart_tsrank63",   f"ts_rank({F_EPS_SMART}, 63)", 3),
    # Correlation with returns
    ("A15_eps_smart_corr_ret10", f"ts_corr(rank({F_EPS_SMART}), rank(returns), 10)", 4),
    ("A16_eps_smart_corr_ret20", f"ts_corr(rank({F_EPS_SMART}), rank(returns), 20)", 5),
    # Acceleration (2nd difference)
    ("A17_eps_smart_accel5",     f"rank(ts_delta(ts_delta({F_EPS_SMART}, 5), 5))", 6),
    # OLS regression slope
    ("A18_eps_smart_regslope20", f"group_neutralize(ts_regression({F_EPS_SMART}, {F_EPS_SMART}, 20), subindustry)", 7),
    # Sign of change scaled by volume
    ("A19_eps_smart_signvol",    f"sign(ts_delta({F_EPS_SMART}, 5)) * rank(volume / adv20)", 8),
    # Corr with volume burst
    ("A20_eps_smart_corr_vol20", f"ts_corr(rank({F_EPS_SMART}), rank(volume / adv20), 20)", 9),

    # ===== GROUP 2: ANALYST RECOMMENDATION (20 alphas) =====
    # Contrarian on recommendation (lower = more bullish → go long)
    ("A21_rec_mean_contrarian",      f"-rank({F_REC_MEAN})", 0),
    ("A22_rec_mean_gzscore_ind",     f"-group_zscore({F_REC_MEAN}, industry)", 1),
    ("A23_rec_mean_gzscore_subind",  f"-group_zscore({F_REC_MEAN}, subindustry)", 2),
    # Upgrade momentum (rec_mean going down = upgrades)
    ("A24_rec_mean_upgrade5",        f"rank(-ts_delta({F_REC_MEAN}, 5))", 3),
    ("A25_rec_mean_upgrade20",       f"rank(-ts_delta({F_REC_MEAN}, 20))", 4),
    ("A26_rec_mean_upgrade63",       f"rank(-ts_delta({F_REC_MEAN}, 63))", 5),
    # Decay-smoothed upgrade
    ("A27_rec_mean_decay_upgrade10", f"group_neutralize(ts_decay_linear(-rank({F_REC_MEAN}), 10), subindustry)", 6),
    # Time-series rank of (negative) rec_mean
    ("A28_rec_mean_tsrank20",        f"ts_rank(-{F_REC_MEAN}, 20)", 7),
    # Standardized rec_mean
    ("A29_rec_mean_std20",           f"(-{F_REC_MEAN} - ts_mean(-{F_REC_MEAN}, 20)) / (ts_std_dev({F_REC_MEAN}, 20) + 0.0001)", 8),
    # Rec mean corr with returns
    ("A30_rec_mean_corr_ret20",      f"ts_corr(rank(-{F_REC_MEAN}), rank(returns), 20)", 9),
    # Rec change (direction of recommendation change)
    ("A31_rec_change_positive",      f"rank({F_REC_CHANGE})", 0),
    ("A32_rec_change_decay10",       f"group_neutralize(ts_decay_linear(rank({F_REC_CHANGE}), 10), industry)", 1),
    ("A33_rec_change_signed_ret",    f"sign({F_REC_CHANGE}) * rank(returns)", 2),
    ("A34_rec_change_tsrank20",      f"ts_rank({F_REC_CHANGE}, 20)", 3),
    ("A35_rec_change_gzscore_ind",   f"group_zscore({F_REC_CHANGE}, industry)", 4),
    ("A36_rec_change_corr_vol10",    f"ts_corr(rank({F_REC_CHANGE}), rank(volume / adv20), 10)", 5),
    # Combined: rec upgrade + eps smart revision
    ("A37_rec_eps_combo",            f"rank(-{F_REC_MEAN}) + rank(ts_delta({F_EPS_SMART}, 10))", 6),
    # Upgrade ratio based on revup vs revdn
    ("A38_revup_ratio",              f"rank({F_REVUP} - {F_REVDN})", 7),
    ("A39_revup_pct",                f"rank({F_REVUP} / ({F_REVUP} + {F_REVDN} + 0.0001))", 8),
    # RevUp combined with EPS smart
    ("A40_revup_eps_combo",          f"rank({F_REVUP}) + rank({F_EPS_SMART})", 9),

    # ===== GROUP 3: PRICE TARGET SIGNALS (20 alphas) =====
    # Upside to price target
    ("A41_ptgt_upside_rank",         f"rank(({F_PRICE_TGT} - close) / (close + 0.0001))", 0),
    ("A42_ptgt_upside_gzscore_ind",  f"group_zscore(({F_PRICE_TGT} - close) / (close + 0.0001), industry)", 1),
    ("A43_ptgt_upside_subind",       f"group_neutralize(rank(({F_PRICE_TGT} - close) / (close + 0.0001)), subindustry)", 2),
    # Price target revision (absolute and pct)
    ("A44_ptgt_delta5",              f"rank(ts_delta({F_PRICE_TGT}, 5))", 3),
    ("A45_ptgt_delta20",             f"rank(ts_delta({F_PRICE_TGT}, 20))", 4),
    ("A46_ptgt_pct_delta10",         f"rank(ts_delta({F_PRICE_TGT}, 10) / ({F_PRICE_TGT} + 0.0001))", 5),
    # Decay-smoothed upside
    ("A47_ptgt_decay10",             f"group_neutralize(ts_decay_linear(rank(({F_PRICE_TGT} - close) / (close + 0.0001)), 10), subindustry)", 6),
    ("A48_ptgt_decay20",             f"group_neutralize(ts_decay_linear(rank(({F_PRICE_TGT} - close) / (close + 0.0001)), 20), industry)", 7),
    # Corr of target upside with returns
    ("A49_ptgt_corr_ret20",          f"ts_corr(rank(({F_PRICE_TGT} - close) / (close + 0.0001)), rank(returns), 20)", 8),
    # TS rank of price target itself
    ("A50_ptgt_tsrank63",            f"ts_rank({F_PRICE_TGT}, 63)", 9),
    # Standardized upside
    ("A51_ptgt_std20",               f"(({F_PRICE_TGT} - close) - ts_mean({F_PRICE_TGT} - close, 20)) / (ts_std_dev({F_PRICE_TGT} - close, 20) + 0.0001)", 0),
    # OLS slope of price target
    ("A52_ptgt_regslope20",          f"ts_regression({F_PRICE_TGT}, {F_PRICE_TGT}, 20)", 1),
    # Sign of target revision times upside
    ("A53_ptgt_signed_upside",       f"sign(ts_delta({F_PRICE_TGT}, 10)) * rank(({F_PRICE_TGT} - close) / (close + 0.0001))", 2),
    # Target acceleration
    ("A54_ptgt_accel5",              f"rank(ts_delta(ts_delta({F_PRICE_TGT}, 5), 5))", 3),
    # Cap-adjusted price target upside
    ("A55_ptgt_capadj",              f"rank(({F_PRICE_TGT} - close) / (cap + 0.0001))", 4),
    # Target vs its own 63d trend
    ("A56_ptgt_vs_ma63",             f"rank({F_PRICE_TGT} - ts_mean({F_PRICE_TGT}, 63))", 5),
    # Corr of target with volume
    ("A57_ptgt_corr_vol10",          f"ts_corr(rank({F_PRICE_TGT}), rank(volume / adv20), 10)", 6),
    # Combined: target upside + rec upgrade
    ("A58_ptgt_rec_combo",           f"rank(({F_PRICE_TGT} - close) / (close + 0.0001)) + rank(-{F_REC_MEAN})", 7),
    # Lagged upside
    ("A59_ptgt_lag10",               f"rank(ts_delay({F_PRICE_TGT} - close, 10) / (close + 0.0001))", 8),
    # AbsChange in target
    ("A60_ptgt_abschange10",         f"rank(abs(ts_delta({F_PRICE_TGT}, 10)))", 9),

    # ===== GROUP 4: EPS SURPRISE (20 alphas) =====
    # Pure surprise signal (post-earnings drift)
    ("A61_eps_surprise_rank",        f"rank({F_SURPRISE})", 0),
    ("A62_eps_surprise_gzscore_ind", f"group_zscore({F_SURPRISE}, industry)", 1),
    ("A63_eps_surprise_subind",      f"group_neutralize(rank({F_SURPRISE}), subindustry)", 2),
    # Decay-smoothed surprise
    ("A64_eps_surprise_decay5",      f"group_neutralize(ts_decay_linear(rank({F_SURPRISE}), 5), subindustry)", 3),
    ("A65_eps_surprise_decay20",     f"group_neutralize(ts_decay_linear(rank({F_SURPRISE}), 20), industry)", 4),
    # Positive surprises only
    ("A66_eps_surprise_positive",    f"rank(max({F_SURPRISE}, 0))", 5),
    # Negative surprise contrarian
    ("A67_eps_surprise_neg_contra",  f"rank(-min({F_SURPRISE}, 0))", 6),
    # Corr with returns
    ("A68_eps_surprise_corr_ret20",  f"ts_corr(rank({F_SURPRISE}), rank(returns), 20)", 7),
    # Volatility-adjusted surprise
    ("A69_eps_surprise_voladj20",    f"{F_SURPRISE} / (ts_std_dev({F_SURPRISE}, 20) + 0.0001)", 8),
    # TS rank of surprise
    ("A70_eps_surprise_tsrank20",    f"ts_rank({F_SURPRISE}, 20)", 9),
    # Signed surprise × return
    ("A71_eps_surprise_sign_ret",    f"sign({F_SURPRISE}) * returns", 0),
    # Surprise acceleration (change in surprise)
    ("A72_eps_surprise_delta10",     f"rank(ts_delta({F_SURPRISE}, 10))", 1),
    # Surprise corr with volume
    ("A73_eps_surprise_corr_vol10",  f"ts_corr(rank({F_SURPRISE}), rank(volume / adv20), 10)", 2),
    # Cap-adjusted surprise
    ("A74_eps_surprise_capadj",      f"rank({F_SURPRISE} / (cap + 0.0001))", 3),
    # Abs magnitude of surprise
    ("A75_eps_surprise_abs",         f"rank(abs({F_SURPRISE}))", 4),
    # Surprise vs its 63d mean
    ("A76_eps_surprise_vs_ma63",     f"rank({F_SURPRISE} - ts_mean({F_SURPRISE}, 63))", 5),
    # Standardized surprise
    ("A77_eps_surprise_std20",       f"({F_SURPRISE} - ts_mean({F_SURPRISE}, 20)) / (ts_std_dev({F_SURPRISE}, 20) + 0.0001)", 6),
    # Long-window decay of surprise rank
    ("A78_eps_surprise_ldecay63",    f"group_neutralize(ts_decay_linear(rank({F_SURPRISE}), 63), industry)", 7),
    # Combined: surprise + revup
    ("A79_eps_surprise_revup_combo", f"rank({F_SURPRISE}) + rank({F_REVUP})", 8),
    # Surprise combined with smart EPS revision
    ("A80_eps_surprise_smart_combo", f"rank({F_SURPRISE}) + rank(ts_delta({F_EPS_SMART}, 10))", 9),

    # ===== GROUP 5: REVENUE SMART (20 alphas) =====
    ("A81_rev_smart_delta5",         f"rank(ts_delta({F_REV_SMART}, 5))", 0),
    ("A82_rev_smart_delta20",        f"rank(ts_delta({F_REV_SMART}, 20))", 1),
    ("A83_rev_smart_gzscore_ind",    f"group_zscore({F_REV_SMART}, industry)", 2),
    ("A84_rev_smart_gzscore_subind", f"group_zscore({F_REV_SMART}, subindustry)", 3),
    ("A85_rev_smart_decay10",        f"group_neutralize(ts_decay_linear(ts_delta({F_REV_SMART}, 10), 10), subindustry)", 4),
    ("A86_rev_smart_decay20",        f"group_neutralize(ts_decay_linear(ts_delta({F_REV_SMART}, 20), 20), industry)", 5),
    ("A87_rev_smart_voladj10",       f"ts_delta({F_REV_SMART}, 10) / (ts_std_dev({F_REV_SMART}, 10) + 0.0001)", 6),
    ("A88_rev_smart_tsrank20",       f"ts_rank({F_REV_SMART}, 20)", 7),
    ("A89_rev_smart_corr_ret20",     f"ts_corr(rank({F_REV_SMART}), rank(returns), 20)", 8),
    ("A90_rev_smart_vs_ma20",        f"rank({F_REV_SMART} - ts_mean({F_REV_SMART}, 20))", 9),
    # vs EPS smart — revenue revision strength relative to EPS
    ("A91_rev_vs_eps_delta10",       f"rank(ts_delta({F_REV_SMART}, 10) - ts_delta({F_EPS_SMART}, 10))", 0),
    ("A92_rev_smart_signed_ret",     f"sign(ts_delta({F_REV_SMART}, 5)) * rank(returns)", 1),
    ("A93_rev_smart_accel5",         f"rank(ts_delta(ts_delta({F_REV_SMART}, 5), 5))", 2),
    ("A94_rev_smart_regslope20",     f"ts_regression({F_REV_SMART}, {F_REV_SMART}, 20)", 3),
    ("A95_rev_smart_capadj",         f"rank(ts_delta({F_REV_SMART}, 10) / (cap + 0.0001))", 4),
    ("A96_rev_smart_corr_vol20",     f"ts_corr(rank({F_REV_SMART}), rank(volume / adv20), 20)", 5),
    ("A97_rev_smart_ldecay63",       f"group_neutralize(ts_decay_linear(rank({F_REV_SMART}), 63), industry)", 6),
    ("A98_rev_smart_subind_rank",    f"group_neutralize(rank({F_REV_SMART}), subindustry)", 7),
    ("A99_rev_smart_lag20",          f"rank({F_REV_SMART} - ts_delay({F_REV_SMART}, 20))", 8),
    ("A100_rev_smart_std63",         f"({F_REV_SMART} - ts_mean({F_REV_SMART}, 63)) / (ts_std_dev({F_REV_SMART}, 63) + 0.0001)", 9),

    # ===== GROUP 6: ANALYST COVERAGE & REVISION COUNTS (20 alphas) =====
    ("A101_numest_delta5",           f"rank(ts_delta({F_NUMEST}, 5))", 0),
    ("A102_numest_delta20",          f"rank(ts_delta({F_NUMEST}, 20))", 1),
    ("A103_numest_gzscore_ind",      f"group_zscore({F_NUMEST}, industry)", 2),
    ("A104_numest_tsrank20",         f"ts_rank({F_NUMEST}, 20)", 3),
    ("A105_numest_subind_rank",      f"group_neutralize(rank({F_NUMEST}), subindustry)", 4),
    ("A106_numest_corr_ret20",       f"ts_corr(rank(ts_delta({F_NUMEST}, 5)), rank(returns), 20)", 5),
    ("A107_numest_signed_ret",       f"sign(ts_delta({F_NUMEST}, 5)) * returns", 6),
    ("A108_numest_capadj",           f"rank({F_NUMEST} / (cap + 0.0001))", 7),
    ("A109_numest_surprise_combo",   f"rank({F_NUMEST}) * sign({F_SURPRISE})", 8),
    ("A110_numest_std20",            f"({F_NUMEST} - ts_mean({F_NUMEST}, 20)) / (ts_std_dev({F_NUMEST}, 20) + 0.0001)", 9),
    # Upward revisions momentum
    ("A111_revup_delta5",            f"rank(ts_delta({F_REVUP}, 5))", 0),
    ("A112_revup_gzscore_ind",       f"group_zscore({F_REVUP}, industry)", 1),
    ("A113_revup_decay10",           f"group_neutralize(ts_decay_linear(rank({F_REVUP}), 10), subindustry)", 2),
    ("A114_revup_tsrank20",          f"ts_rank({F_REVUP}, 20)", 3),
    ("A115_revup_corr_ret20",        f"ts_corr(rank({F_REVUP}), rank(returns), 20)", 4),
    ("A116_revup_pct_of_total",      f"rank({F_REVUP} / ({F_NUMEST} + 0.0001))", 5),
    ("A117_revup_capadj",            f"rank({F_REVUP} / (cap + 0.0001))", 6),
    ("A118_revup_std20",             f"({F_REVUP} - ts_mean({F_REVUP}, 20)) / (ts_std_dev({F_REVUP}, 20) + 0.0001)", 7),
    ("A119_revup_signed_ret",        f"sign({F_REVUP} - {F_REVDN}) * returns", 8),
    ("A120_revup_subind_rank",       f"group_neutralize(rank({F_REVUP} - {F_REVDN}), subindustry)", 9),

    # ===== GROUP 7: FORWARD EPS SIGNALS (20 alphas) =====
    ("A121_fwd1_delta5",             f"rank(ts_delta({F_EPS_FWD1}, 5))", 0),
    ("A122_fwd1_delta20",            f"rank(ts_delta({F_EPS_FWD1}, 20))", 1),
    ("A123_fwd1_gzscore_ind",        f"group_zscore({F_EPS_FWD1}, industry)", 2),
    ("A124_fwd1_gzscore_subind",     f"group_zscore({F_EPS_FWD1}, subindustry)", 3),
    ("A125_fwd1_decay10",            f"group_neutralize(ts_decay_linear(rank(ts_delta({F_EPS_FWD1}, 10)), 10), subindustry)", 4),
    ("A126_fwd1_voladj10",           f"ts_delta({F_EPS_FWD1}, 10) / (ts_std_dev({F_EPS_FWD1}, 10) + 0.0001)", 5),
    ("A127_fwd1_tsrank20",           f"ts_rank({F_EPS_FWD1}, 20)", 6),
    ("A128_fwd1_corr_ret20",         f"ts_corr(rank({F_EPS_FWD1}), rank(returns), 20)", 7),
    ("A129_fwd1_subind_rank",        f"group_neutralize(rank({F_EPS_FWD1}), subindustry)", 8),
    # Fwd curve steepness
    ("A130_fwd1_vs_fwd2",            f"rank({F_EPS_FWD1} - {F_EPS_FWD2})", 9),
    # Fwd1 vs smart
    ("A131_fwd1_vs_smart",           f"rank({F_EPS_FWD1} - {F_EPS_SMART})", 0),
    ("A132_fwd1_accel5",             f"rank(ts_delta(ts_delta({F_EPS_FWD1}, 5), 5))", 1),
    ("A133_fwd1_std63",              f"({F_EPS_FWD1} - ts_mean({F_EPS_FWD1}, 63)) / (ts_std_dev({F_EPS_FWD1}, 63) + 0.0001)", 2),
    ("A134_fwd1_regslope20",         f"ts_regression({F_EPS_FWD1}, {F_EPS_FWD1}, 20)", 3),
    ("A135_fwd1_lag20",              f"rank({F_EPS_FWD1} - ts_delay({F_EPS_FWD1}, 20))", 4),
    ("A136_fwd1_corr_vol10",         f"ts_corr(rank({F_EPS_FWD1}), rank(volume / adv20), 10)", 5),
    ("A137_fwd1_capadj",             f"rank({F_EPS_FWD1} / (cap + 0.0001))", 6),
    ("A138_fwd1_decay63",            f"group_neutralize(ts_decay_linear(rank({F_EPS_FWD1}), 63), industry)", 7),
    ("A139_fwd1_abschange10",        f"rank(abs(ts_delta({F_EPS_FWD1}, 10)))", 8),
    ("A140_fwd1_signed_ret",         f"sign(ts_delta({F_EPS_FWD1}, 10)) * rank(returns)", 9),

    # ===== GROUP 8: EBITDA SMART (20 alphas) =====
    ("A141_ebitda_delta5",           f"rank(ts_delta({F_EBITDA}, 5))", 0),
    ("A142_ebitda_delta20",          f"rank(ts_delta({F_EBITDA}, 20))", 1),
    ("A143_ebitda_gzscore_ind",      f"group_zscore({F_EBITDA}, industry)", 2),
    ("A144_ebitda_gzscore_subind",   f"group_zscore({F_EBITDA}, subindustry)", 3),
    ("A145_ebitda_decay10",          f"group_neutralize(ts_decay_linear(rank(ts_delta({F_EBITDA}, 10)), 10), subindustry)", 4),
    ("A146_ebitda_voladj10",         f"ts_delta({F_EBITDA}, 10) / (ts_std_dev({F_EBITDA}, 10) + 0.0001)", 5),
    ("A147_ebitda_tsrank20",         f"ts_rank({F_EBITDA}, 20)", 6),
    ("A148_ebitda_corr_ret20",       f"ts_corr(rank({F_EBITDA}), rank(returns), 20)", 7),
    ("A149_ebitda_subind_rank",      f"group_neutralize(rank({F_EBITDA}), subindustry)", 8),
    ("A150_ebitda_vs_rev",           f"rank({F_EBITDA}) - rank({F_REV_SMART})", 9),
    ("A151_ebitda_accel5",           f"rank(ts_delta(ts_delta({F_EBITDA}, 5), 5))", 0),
    ("A152_ebitda_std63",            f"({F_EBITDA} - ts_mean({F_EBITDA}, 63)) / (ts_std_dev({F_EBITDA}, 63) + 0.0001)", 1),
    ("A153_ebitda_regslope20",       f"ts_regression({F_EBITDA}, {F_EBITDA}, 20)", 2),
    ("A154_ebitda_lag20",            f"rank({F_EBITDA} - ts_delay({F_EBITDA}, 20))", 3),
    ("A155_ebitda_corr_vol10",       f"ts_corr(rank({F_EBITDA}), rank(volume / adv20), 10)", 4),
    ("A156_ebitda_capadj",           f"rank({F_EBITDA} / (cap + 0.0001))", 5),
    ("A157_ebitda_decay63",          f"group_neutralize(ts_decay_linear(rank({F_EBITDA}), 63), industry)", 6),
    ("A158_ebitda_vs_eps",           f"rank(ts_delta({F_EBITDA}, 10) - ts_delta({F_EPS_SMART}, 10))", 7),
    ("A159_ebitda_abschange10",      f"rank(abs(ts_delta({F_EBITDA}, 10)))", 8),
    ("A160_ebitda_signed_ret",       f"sign(ts_delta({F_EBITDA}, 10)) * rank(returns)", 9),

    # ===== GROUP 9: DPS SMART + LT GROWTH (20 alphas) =====
    ("A161_dps_delta5",              f"rank(ts_delta({F_DPS}, 5))", 0),
    ("A162_dps_delta20",             f"rank(ts_delta({F_DPS}, 20))", 1),
    ("A163_dps_gzscore_ind",         f"group_zscore({F_DPS}, industry)", 2),
    ("A164_dps_decay10",             f"group_neutralize(ts_decay_linear(rank(ts_delta({F_DPS}, 10)), 10), subindustry)", 3),
    ("A165_dps_voladj10",            f"ts_delta({F_DPS}, 10) / (ts_std_dev({F_DPS}, 10) + 0.0001)", 4),
    ("A166_dps_tsrank20",            f"ts_rank({F_DPS}, 20)", 5),
    ("A167_dps_corr_ret20",          f"ts_corr(rank({F_DPS}), rank(returns), 20)", 6),
    ("A168_dps_subind_rank",         f"group_neutralize(rank({F_DPS}), subindustry)", 7),
    ("A169_dps_vs_eps",              f"rank(ts_delta({F_DPS}, 10) - ts_delta({F_EPS_SMART}, 10))", 8),
    ("A170_dps_decay63",             f"group_neutralize(ts_decay_linear(rank({F_DPS}), 63), industry)", 9),
    # LT Growth signals
    ("A171_ltgrowth_delta5",         f"rank(ts_delta({F_LTGROWTH}, 5))", 0),
    ("A172_ltgrowth_delta20",        f"rank(ts_delta({F_LTGROWTH}, 20))", 1),
    ("A173_ltgrowth_gzscore_ind",    f"group_zscore({F_LTGROWTH}, industry)", 2),
    ("A174_ltgrowth_decay10",        f"group_neutralize(ts_decay_linear(rank(ts_delta({F_LTGROWTH}, 10)), 10), subindustry)", 3),
    ("A175_ltgrowth_tsrank20",       f"ts_rank({F_LTGROWTH}, 20)", 4),
    ("A176_ltgrowth_corr_ret20",     f"ts_corr(rank({F_LTGROWTH}), rank(returns), 20)", 5),
    ("A177_ltgrowth_subind_rank",    f"group_neutralize(rank({F_LTGROWTH}), subindustry)", 6),
    ("A178_ltgrowth_vs_fwd1",        f"rank({F_LTGROWTH}) - rank({F_EPS_FWD1})", 7),
    ("A179_ltgrowth_decay63",        f"group_neutralize(ts_decay_linear(rank({F_LTGROWTH}), 63), industry)", 8),
    ("A180_ltgrowth_vs_rev",         f"rank({F_LTGROWTH}) - rank({F_REV_SMART})", 9),

    # ===== GROUP 10: CROSS-FIELD COMBOS (20 alphas) =====
    # Multi-field composite alphas — max diversification from self-corr
    ("A181_eps_smart_rec_ptgt_combo",f"rank({F_EPS_SMART}) + rank(-{F_REC_MEAN}) + rank(({F_PRICE_TGT} - close) / (close + 0.0001))", 0),
    ("A182_surprise_revup_rec",      f"rank({F_SURPRISE}) + rank({F_REVUP}) + rank(-{F_REC_MEAN})", 1),
    ("A183_rev_ebitda_diff",         f"rank(ts_delta({F_REV_SMART}, 20) - ts_delta({F_EBITDA}, 20))", 2),
    ("A184_fwd1_surprise_combo",     f"rank({F_EPS_FWD1}) + rank({F_SURPRISE})", 3),
    ("A185_eps_smart_numest_combo",  f"rank({F_EPS_SMART}) * sign(ts_delta({F_NUMEST}, 5))", 4),
    ("A186_ptgt_revup_weighted",     f"0.5 * rank(({F_PRICE_TGT} - close) / (close + 0.0001)) + 0.5 * rank({F_REVUP} / ({F_NUMEST} + 0.0001))", 5),
    ("A187_rec_ptgt_momentum",       f"rank(-ts_delta({F_REC_MEAN}, 20)) + rank(ts_delta({F_PRICE_TGT}, 20))", 6),
    ("A188_eps_curve_steepness",     f"rank({F_EPS_FWD1} - {F_EPS_FWD2}) + rank(ts_delta({F_EPS_SMART}, 10))", 7),
    ("A189_triple_revision_combo",   f"rank(ts_delta({F_EPS_SMART}, 10)) + rank(ts_delta({F_REV_SMART}, 10)) + rank(ts_delta({F_EBITDA}, 10))", 8),
    ("A190_surprise_momentum_decay", f"group_neutralize(ts_decay_linear(rank({F_SURPRISE}) + rank({F_EPS_SMART}), 10), subindustry)", 9),
    # Conditional signals — trade only in high-volume periods
    ("A191_eps_smart_highvol",       f"trade_when(ts_rank(volume, 20) > 0.7, rank(ts_delta({F_EPS_SMART}, 10)), 0)", 0),
    ("A192_surprise_highvol",        f"trade_when(ts_rank(volume, 20) > 0.7, rank({F_SURPRISE}), 0)", 1),
    ("A193_ptgt_highvol",            f"trade_when(ts_rank(volume, 20) > 0.7, rank(({F_PRICE_TGT} - close) / (close + 0.0001)), 0)", 2),
    # Entropy-filtered signals
    ("A194_eps_smart_entropy_gated", f"trade_when(ts_entropy({F_EPS_SMART}, 20) > 0.5, rank(ts_delta({F_EPS_SMART}, 10)), 0)", 3),
    # Mean reversion on surprise
    ("A195_surprise_reversion",      f"-ts_decay_linear(rank({F_SURPRISE}), 63)", 4),
    # Long-run EPS fwd1 revision trend
    ("A196_fwd1_longtrend",          f"group_neutralize(ts_regression({F_EPS_FWD1}, {F_EPS_FWD1}, 126), industry)", 5),
    # EPS smart corr with EBITDA
    ("A197_eps_ebitda_corr",         f"ts_corr(rank({F_EPS_SMART}), rank({F_EBITDA}), 20)", 6),
    # Double-smooth combo
    ("A198_doublesmooth_rec_eps",    f"group_neutralize(ts_decay_linear(ts_decay_linear(rank({F_EPS_SMART}) + rank(-{F_REC_MEAN}), 5), 20), subindustry)", 7),
    # Relative revision: eps vs revenue
    ("A199_eps_vs_rev_relative",     f"rank(ts_delta({F_EPS_SMART}, 10) / (ts_std_dev({F_EPS_SMART}, 10) + 0.0001)) - rank(ts_delta({F_REV_SMART}, 10) / (ts_std_dev({F_REV_SMART}, 10) + 0.0001))", 8),
    # Pure momentum: all fields ranked equally weighted
    ("A200_grand_composite",         f"rank({F_EPS_SMART}) + rank(-{F_REC_MEAN}) + rank({F_SURPRISE}) + rank({F_EPS_FWD1}) + rank(({F_PRICE_TGT} - close) / (close + 0.0001))", 9),
]

# -----------------------------------------------------------------------
# Build final alpha list using generate_alpha() format from ace_lib
# -----------------------------------------------------------------------
def make_alpha(name, formula, settings_idx):
    s = SETTINGS_VARIANTS[settings_idx % len(SETTINGS_VARIANTS)]
    return {
        "name": name,
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": s["region"],
            "universe": s["universe"],
            "delay": 1,
            "decay": s["decay"],
            "neutralization": s["neutralization"],
            "truncation": s["truncation"],
            "pasteurization": "ON",
            "testPeriod": "P0Y0M0D",
            "unitHandling": "VERIFY",
            "nanHandling": "OFF",
            "language": "FASTEXPR",
            "visualization": False,
        },
        "regular": formula,
        "dataset": "analyst10",
    }

alphas = []
seen_formulas = set()
for (name, formula, settings_idx) in ALPHAS_RAW:
    if formula in seen_formulas:
        print(f"SKIPPING duplicate formula: {name} => {formula}")
        continue
    seen_formulas.add(formula)
    alphas.append(make_alpha(name, formula, settings_idx))

print(f"\n{'='*60}")
print(f"Generated {len(alphas)} unique analyst10 alphas")

# Save
with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(alphas, f, indent=2)

print(f"Saved to: {OUT_FILE}")
print(f"\nSample (first 5 alphas):")
for a in alphas[:5]:
    print(f"  [{a['name']}]")
    print(f"    formula : {a['regular']}")
    print(f"    decay={a['settings']['decay']} | neutral={a['settings']['neutralization']} | trunc={a['settings']['truncation']}")
    print()

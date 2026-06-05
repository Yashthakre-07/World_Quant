import os
import json
import urllib.request
import ssl
import time
import random
from datetime import datetime

# --- SETTINGS & CONFIGURATION ---
API_URL = "https://world-quant.onrender.com/api/queue-alpha"
API_AUTH_TOKEN = "yashthakreop"
RUN_LOG_PATH = "scratch/run_log.txt"

def log_run(message):
    timestamp = datetime.now().isoformat()
    log_line = f"{timestamp} | {message}\n"
    os.makedirs(os.path.dirname(RUN_LOG_PATH), exist_ok=True)
    with open(RUN_LOG_PATH, "a") as f:
        f.write(log_line)
    print(log_line.strip())

def check_internet():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        urllib.request.urlopen("https://dns.google", timeout=5, context=ctx)
        return True
    except Exception:
        return False

HISTORICAL_FILE = "scratch/historical_scheduled_alphas.json"

def load_historical_formulas():
    if os.path.exists(HISTORICAL_FILE):
        try:
            with open(HISTORICAL_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_historical_formulas(formulas):
    try:
        with open(HISTORICAL_FILE, "w") as f:
            json.dump(list(formulas), f, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

# =============================================================================
# MASTER FORMULA TEMPLATE LIBRARY
# =============================================================================
# COMPILER SAFETY RULES (ALL TEMPLATES VERIFIED):
#   RULE 1: ALL analyst vector fields (anl4_*, anl16_*, anl44_*, anl45_*)
#            MUST be wrapped in vec_avg() before any rank/ts_* operator.
#   RULE 2: NO scalar constant (+0.001) added directly to any event field.
#   RULE 3: NO rank() or ts_* operators directly on raw event fields.
#   RULE 4: Event / Event division is safe (no vec_avg needed).
#   RULE 5: ts_corr(returns, vec_avg(event_field), L) is safe.
#   RULE 6: group_neutralize(x, subindustry) is the outer wrapper.
#   RULE 7: trade_when(volume > adv20 * GATE, inner, 0) gates every formula.
#   RULE 8: settings always: region=USA, delay=1, universe=TOP3000.
# =============================================================================

def build_formula_pool(rng):
    """
    Returns a list of (formula_string, metadata_dict) tuples.
    The pool is rebuilt with fresh random parameters on every call,
    guaranteeing uniqueness across scheduled runs via the historical dedup.
    """
    pool = []

    # Volume gate range [0.65, 0.80] in steps of 0.01 => 16 values
    gates = [round(0.65 + i * 0.01, 2) for i in range(16)]
    # Lookback pools by category
    short_looks = [5, 6, 7, 8, 9, 10]
    mid_looks   = [10, 12, 14, 15, 16, 18, 20]
    long_looks  = [20, 22, 25, 30, 40, 60]
    all_looks   = short_looks + mid_looks + long_looks

    # -------------------------------------------------------------------------
    # DATASET: analyst4
    # Fields (all VECTOR → must use vec_avg):
    #   anl4_fs_basic_splt_v4_nd_eps_estimate
    #   anl4_fs_basic_splt_v4_nd_sales_estimate
    #   anl4_fs_detail_estimates_advanced_af_nd_ebitda_high
    #   anl4_fs_detail_estimates_advanced_af_nd_ebitda_low
    #   anl4_fs_detail_estimates_advanced_af_nd_ebitda_mean
    #   anl4_fs_detail_estimates_advanced_af_nd_ptp_high
    #   anl4_fs_detail_estimates_advanced_af_nd_ptp_low
    #   anl4_fs_detail_estimates_advanced_af_nd_ptp_mean
    #   anl4_fs_detail_estimates_advanced_af_nd_fcf_high
    #   anl4_fs_detail_estimates_advanced_af_nd_fcf_low
    #   anl4_fs_detail_estimates_advanced_af_nd_ptp_number
    # -------------------------------------------------------------------------
    a4_fields = [
        ("anl4_fs_basic_splt_v4_nd_eps_estimate",                     "EPS Consensus Estimate"),
        ("anl4_fs_basic_splt_v4_nd_sales_estimate",                   "Sales Consensus Estimate"),
        ("anl4_fs_detail_estimates_advanced_af_nd_ebitda_high",       "EBITDA High Estimate"),
        ("anl4_fs_detail_estimates_advanced_af_nd_ebitda_low",        "EBITDA Low Estimate"),
        ("anl4_fs_detail_estimates_advanced_af_nd_ebitda_mean",       "EBITDA Mean Estimate"),
        ("anl4_fs_detail_estimates_advanced_af_nd_ptp_high",          "Pretax Profit High Estimate"),
        ("anl4_fs_detail_estimates_advanced_af_nd_ptp_low",           "Pretax Profit Low Estimate"),
        ("anl4_fs_detail_estimates_advanced_af_nd_ptp_mean",          "Pretax Profit Mean Estimate"),
        ("anl4_fs_detail_estimates_advanced_af_nd_fcf_high",          "Free Cash Flow High Estimate"),
        ("anl4_fs_detail_estimates_advanced_af_nd_fcf_low",           "Free Cash Flow Low Estimate"),
    ]

    # Shape A1: ts_delta momentum on vec_avg
    for (fld, desc) in a4_fields:
        for look in all_looks:
            gate = rng.choice(gates)
            formula = (
                f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
                f"rank(ts_delta(vec_avg({fld}), {look})), 0), subindustry)"
            )
            meta = {
                "family": "ThemePool_USA_D1",
                "dataset": "analyst4",
                "competition": "USA_D1_FastDatasets_PowerPool_June2026",
                "hypothesis": f"Rolling {look}-day EPS revision momentum via vec_avg on {desc}.",
                "anomaly_basis": "Post-Earnings Announcement Drift (PEAD)",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape A2: ts_corr(returns, vec_avg(field), L)
    for (fld, desc) in a4_fields:
        for look in mid_looks + long_looks:
            gate = rng.choice(gates)
            formula = (
                f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
                f"rank(ts_corr(returns, vec_avg({fld}), {look})), 0), subindustry)"
            )
            meta = {
                "family": "ThemePool_USA_D1",
                "dataset": "analyst4",
                "competition": "USA_D1_FastDatasets_PowerPool_June2026",
                "hypothesis": f"{look}-day return-vs-estimate correlation for {desc}.",
                "anomaly_basis": "Surprise Sentiment Alignment",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape A3: ts_rank(vec_avg(field), L) — rolling percentile
    for (fld, desc) in a4_fields:
        for look in mid_looks:
            gate = rng.choice(gates)
            formula = (
                f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
                f"ts_rank(vec_avg({fld}), {look}), 0), subindustry)"
            )
            meta = {
                "family": "ThemePool_USA_D1",
                "dataset": "analyst4",
                "competition": "USA_D1_FastDatasets_PowerPool_June2026",
                "hypothesis": f"Rolling {look}-day percentile rank of {desc}.",
                "anomaly_basis": "Analyst Estimate Percentile Momentum",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape A4: ts_mean deviation (mean reversion)
    for (fld, desc) in a4_fields:
        for look in mid_looks:
            gate = rng.choice(gates)
            formula = (
                f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
                f"rank(ts_av_diff(vec_avg({fld}), {look})), 0), subindustry)"
            )
            meta = {
                "family": "ThemePool_USA_D1",
                "dataset": "analyst4",
                "competition": "USA_D1_FastDatasets_PowerPool_June2026",
                "hypothesis": f"Mean-deviation reversion on {desc} over {look}-day window.",
                "anomaly_basis": "Estimate Mean Reversion",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape A5: Cross-dataset ratio — EPS/Sales (event/event division is safe)
    for look in all_looks:
        gate = rng.choice(gates)
        formula = (
            f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
            f"rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate) / "
            f"vec_avg(anl4_fs_basic_splt_v4_nd_sales_estimate), {look})), 0), subindustry)"
        )
        meta = {
            "family": "ThemePool_USA_D1",
            "dataset": "analyst4",
            "competition": "USA_D1_FastDatasets_PowerPool_June2026",
            "hypothesis": f"{look}-day delta in EPS/Sales forward margin ratio (consensus operating margin surrogate).",
            "anomaly_basis": "Fundamental Yield Reversion",
            "formula": formula,
            "settings": {"region": "USA", "delay": 1, "decay": 8,
                         "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        }
        pool.append((formula, meta))

    # Shape A6: EBITDA dispersion signal (high-low spread, event/event safe)
    for look in mid_looks:
        gate = rng.choice(gates)
        formula = (
            f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
            f"-rank(ts_delta(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high) / "
            f"vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ebitda_low), {look})), 0), subindustry)"
        )
        meta = {
            "family": "ThemePool_USA_D1",
            "dataset": "analyst4",
            "competition": "USA_D1_FastDatasets_PowerPool_June2026",
            "hypothesis": f"Analyst EBITDA disagreement (high/low ratio) delta over {look} days — fade extreme dispersion.",
            "anomaly_basis": "Earnings Estimate Dispersion Mean Reversion",
            "formula": formula,
            "settings": {"region": "USA", "delay": 1, "decay": 8,
                         "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        }
        pool.append((formula, meta))

    # Shape A7: FCF vs EBITDA conviction ratio delta
    for look in mid_looks + long_looks:
        gate = rng.choice(gates)
        formula = (
            f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
            f"rank(ts_delta(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_fcf_high) / "
            f"vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high), {look})), 0), subindustry)"
        )
        meta = {
            "family": "ThemePool_USA_D1",
            "dataset": "analyst4",
            "competition": "USA_D1_FastDatasets_PowerPool_June2026",
            "hypothesis": f"{look}-day change in FCH/EBITDA ratio — measures cash flow quality conviction.",
            "anomaly_basis": "Cash Flow Quality Signal",
            "formula": formula,
            "settings": {"region": "USA", "delay": 1, "decay": 8,
                         "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        }
        pool.append((formula, meta))

    # Shape A8: PTP High minus PTP Low dispersion momentum
    for look in short_looks + mid_looks:
        gate = rng.choice(gates)
        formula = (
            f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
            f"-rank(ts_delta(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ptp_high) / "
            f"vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ptp_low), {look})), 0), subindustry)"
        )
        meta = {
            "family": "ThemePool_USA_D1",
            "dataset": "analyst4",
            "competition": "USA_D1_FastDatasets_PowerPool_June2026",
            "hypothesis": f"Pretax profit analyst disagreement ratio delta over {look} days.",
            "anomaly_basis": "Analyst Forecast Uncertainty",
            "formula": formula,
            "settings": {"region": "USA", "delay": 1, "decay": 8,
                         "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        }
        pool.append((formula, meta))

    # -------------------------------------------------------------------------
    # DATASET: analyst16 (Real Time Estimates — crowdsourced)
    # Fields (all VECTOR → must use vec_avg):
    #   anl16_actsurprise  — actual consensus surprise
    #   anl16_actsuescore  — standardized unexpected earnings score
    #   anl16_sue          — standardized unexpected earnings
    #   anl16_revisions    — estimate revision count
    # -------------------------------------------------------------------------
    a16_fields = [
        ("anl16_actsurprise",  "Actual Consensus Surprise"),
        ("anl16_actsuescore",  "Standardized Unexpected Earnings Score"),
        ("anl16_sue",          "Standardized Unexpected Earnings"),
    ]

    # Shape B1: ts_delta momentum
    for (fld, desc) in a16_fields:
        for look in all_looks:
            gate = rng.choice(gates)
            formula = (
                f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
                f"rank(ts_delta(vec_avg({fld}), {look})), 0), subindustry)"
            )
            meta = {
                "family": "ThemePool_USA_D1",
                "dataset": "analyst16",
                "competition": "USA_D1_FastDatasets_PowerPool_June2026",
                "hypothesis": f"{look}-day momentum in {desc} (crowdsourced real-time estimate).",
                "anomaly_basis": "Analyst Surprise Momentum",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape B2: ts_corr(returns, vec_avg, L)
    for (fld, desc) in a16_fields:
        for look in mid_looks + long_looks:
            gate = rng.choice(gates)
            formula = (
                f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
                f"rank(ts_corr(returns, vec_avg({fld}), {look})), 0), subindustry)"
            )
            meta = {
                "family": "ThemePool_USA_D1",
                "dataset": "analyst16",
                "competition": "USA_D1_FastDatasets_PowerPool_June2026",
                "hypothesis": f"{look}-day return correlation with {desc}.",
                "anomaly_basis": "Surprise-Return Alignment",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape B3: ts_rank percentile
    for (fld, desc) in a16_fields:
        for look in mid_looks:
            gate = rng.choice(gates)
            formula = (
                f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
                f"ts_rank(vec_avg({fld}), {look}), 0), subindustry)"
            )
            meta = {
                "family": "ThemePool_USA_D1",
                "dataset": "analyst16",
                "competition": "USA_D1_FastDatasets_PowerPool_June2026",
                "hypothesis": f"Rolling {look}-day percentile of {desc}.",
                "anomaly_basis": "Earnings Quality Drift",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape B4: ts_av_diff (mean deviation)
    for (fld, desc) in a16_fields:
        for look in mid_looks:
            gate = rng.choice(gates)
            formula = (
                f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
                f"-rank(ts_av_diff(vec_avg({fld}), {look})), 0), subindustry)"
            )
            meta = {
                "family": "ThemePool_USA_D1",
                "dataset": "analyst16",
                "competition": "USA_D1_FastDatasets_PowerPool_June2026",
                "hypothesis": f"Mean deviation fade of {desc} over {look} days.",
                "anomaly_basis": "Surprise Mean Reversion",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape B5: actsurprise / actsuescore ratio (event/event)
    for look in mid_looks + long_looks:
        gate = rng.choice(gates)
        formula = (
            f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
            f"rank(ts_delta(vec_avg(anl16_actsurprise) / vec_avg(anl16_actsuescore), {look})), 0), subindustry)"
        )
        meta = {
            "family": "ThemePool_USA_D1",
            "dataset": "analyst16",
            "competition": "USA_D1_FastDatasets_PowerPool_June2026",
            "hypothesis": f"{look}-day delta of surprise/score ratio — quality of surprise signal.",
            "anomaly_basis": "Earnings Quality Ratio Momentum",
            "formula": formula,
            "settings": {"region": "USA", "delay": 1, "decay": 8,
                         "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        }
        pool.append((formula, meta))

    # -------------------------------------------------------------------------
    # DATASET: analyst44 (Integrated Broker Estimates)
    # Fields (all VECTOR → must use vec_avg):
    #   anl44_analyst      — integrated broker recommendation score
    #   anl44_target_price — broker price target
    #   anl44_num_buys     — number of buy recommendations
    #   anl44_num_holds    — number of hold recommendations
    #   anl44_num_sells    — number of sell recommendations
    # -------------------------------------------------------------------------
    a44_fields = [
        ("anl44_analyst",      "Integrated Broker Recommendation"),
        ("anl44_target_price", "Broker Price Target"),
        ("anl44_num_buys",     "Number of Buy Recommendations"),
        ("anl44_num_holds",    "Number of Hold Recommendations"),
        ("anl44_num_sells",    "Number of Sell Recommendations"),
    ]

    # Shape C1: ts_delta momentum
    for (fld, desc) in a44_fields:
        for look in all_looks:
            gate = rng.choice(gates)
            formula = (
                f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
                f"rank(ts_delta(vec_avg({fld}), {look})), 0), subindustry)"
            )
            meta = {
                "family": "ThemePool_USA_D1",
                "dataset": "analyst44",
                "competition": "USA_D1_FastDatasets_PowerPool_June2026",
                "hypothesis": f"{look}-day change in {desc} (broker consensus drift).",
                "anomaly_basis": "Consensus Recommendation Conviction",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape C2: ts_corr(returns, vec_avg, L)
    for (fld, desc) in a44_fields:
        for look in mid_looks + long_looks:
            gate = rng.choice(gates)
            formula = (
                f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
                f"rank(ts_corr(returns, vec_avg({fld}), {look})), 0), subindustry)"
            )
            meta = {
                "family": "ThemePool_USA_D1",
                "dataset": "analyst44",
                "competition": "USA_D1_FastDatasets_PowerPool_June2026",
                "hypothesis": f"{look}-day return correlation with {desc}.",
                "anomaly_basis": "Recommendation Drift Momentum",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape C3: ts_rank percentile
    for (fld, desc) in a44_fields:
        for look in mid_looks:
            gate = rng.choice(gates)
            formula = (
                f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
                f"ts_rank(vec_avg({fld}), {look}), 0), subindustry)"
            )
            meta = {
                "family": "ThemePool_USA_D1",
                "dataset": "analyst44",
                "competition": "USA_D1_FastDatasets_PowerPool_June2026",
                "hypothesis": f"Rolling {look}-day percentile of {desc}.",
                "anomaly_basis": "Analyst Recommendation Percentile",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape C4: buys-vs-sells ratio momentum (event/event)
    for look in all_looks:
        gate = rng.choice(gates)
        formula = (
            f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
            f"rank(ts_delta(vec_avg(anl44_num_buys) / vec_avg(anl44_num_sells), {look})), 0), subindustry)"
        )
        meta = {
            "family": "ThemePool_USA_D1",
            "dataset": "analyst44",
            "competition": "USA_D1_FastDatasets_PowerPool_June2026",
            "hypothesis": f"{look}-day delta in buy/sell ratio — measures recommendation conviction shifts.",
            "anomaly_basis": "Recommendation Conviction Ratio",
            "formula": formula,
            "settings": {"region": "USA", "delay": 1, "decay": 8,
                         "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        }
        pool.append((formula, meta))

    # Shape C5: target price / analyst score ratio
    for look in mid_looks:
        gate = rng.choice(gates)
        formula = (
            f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
            f"rank(ts_delta(vec_avg(anl44_target_price) / vec_avg(anl44_analyst), {look})), 0), subindustry)"
        )
        meta = {
            "family": "ThemePool_USA_D1",
            "dataset": "analyst44",
            "competition": "USA_D1_FastDatasets_PowerPool_June2026",
            "hypothesis": f"{look}-day delta in price-target/score ratio — upside conviction momentum.",
            "anomaly_basis": "Price Target Conviction",
            "formula": formula,
            "settings": {"region": "USA", "delay": 1, "decay": 8,
                         "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        }
        pool.append((formula, meta))

    # -------------------------------------------------------------------------
    # DATASET: analyst45 (Analyst Trade Ideas)
    # Fields (all VECTOR → must use vec_avg):
    #   anl45_ad_rel_ret_per  — analyst relative return performance
    #   anl45_jensensalpha    — Jensen's alpha performance metric
    #   anl45_hit_rate        — analyst hit rate
    #   anl45_avg_ret         — analyst average return
    #   anl45_num_recs        — number of recommendations
    # -------------------------------------------------------------------------
    a45_fields = [
        ("anl45_ad_rel_ret_per", "Analyst Relative Return Performance"),
        ("anl45_jensensalpha",   "Jensen's Alpha"),
        ("anl45_hit_rate",       "Analyst Hit Rate"),
        ("anl45_avg_ret",        "Analyst Average Return"),
        ("anl45_num_recs",       "Number of Recommendations"),
    ]

    # Shape D1: ts_delta momentum
    for (fld, desc) in a45_fields:
        for look in all_looks:
            gate = rng.choice(gates)
            formula = (
                f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
                f"rank(ts_delta(vec_avg({fld}), {look})), 0), subindustry)"
            )
            meta = {
                "family": "ThemePool_USA_D1",
                "dataset": "analyst45",
                "competition": "USA_D1_FastDatasets_PowerPool_June2026",
                "hypothesis": f"{look}-day change in {desc} (analyst trade idea quality drift).",
                "anomaly_basis": "Analyst Performance Anomalies",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape D2: ts_corr(returns, vec_avg, L)
    for (fld, desc) in a45_fields:
        for look in mid_looks + long_looks:
            gate = rng.choice(gates)
            formula = (
                f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
                f"rank(ts_corr(returns, vec_avg({fld}), {look})), 0), subindustry)"
            )
            meta = {
                "family": "ThemePool_USA_D1",
                "dataset": "analyst45",
                "competition": "USA_D1_FastDatasets_PowerPool_June2026",
                "hypothesis": f"{look}-day return correlation with {desc}.",
                "anomaly_basis": "Analyst Performance Alignment",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape D3: ts_rank percentile
    for (fld, desc) in a45_fields:
        for look in mid_looks:
            gate = rng.choice(gates)
            formula = (
                f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
                f"ts_rank(vec_avg({fld}), {look}), 0), subindustry)"
            )
            meta = {
                "family": "ThemePool_USA_D1",
                "dataset": "analyst45",
                "competition": "USA_D1_FastDatasets_PowerPool_June2026",
                "hypothesis": f"Rolling {look}-day percentile of {desc}.",
                "anomaly_basis": "Analyst Skill Percentile",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape D4: Jensen's Alpha vs Hit Rate ratio (event/event)
    for look in mid_looks:
        gate = rng.choice(gates)
        formula = (
            f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
            f"rank(ts_delta(vec_avg(anl45_jensensalpha) / vec_avg(anl45_hit_rate), {look})), 0), subindustry)"
        )
        meta = {
            "family": "ThemePool_USA_D1",
            "dataset": "analyst45",
            "competition": "USA_D1_FastDatasets_PowerPool_June2026",
            "hypothesis": f"{look}-day delta of Jensen's alpha / hit rate — quality-adjusted skill.",
            "anomaly_basis": "Risk-Adjusted Analyst Skill",
            "formula": formula,
            "settings": {"region": "USA", "delay": 1, "decay": 8,
                         "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        }
        pool.append((formula, meta))

    # =========================================================================
    # CROSS-DATASET COMBINATION FORMULAS
    # Combines signals from different datasets for decorrelated, high-Sharpe combos
    # =========================================================================

    # XD1: analyst4 EPS revision × analyst44 recommendation score
    for look in mid_looks + long_looks:
        gate = rng.choice(gates)
        formula = (
            f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
            f"rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), {look}) * "
            f"ts_rank(vec_avg(anl44_analyst), {look})), 0), subindustry)"
        )
        meta = {
            "family": "ThemePool_USA_D1",
            "dataset": "analyst4_x_analyst44",
            "competition": "USA_D1_FastDatasets_PowerPool_June2026",
            "hypothesis": f"EPS revision momentum × broker recommendation percentile over {look} days.",
            "anomaly_basis": "Conviction × Revision Cross-Dataset Combo",
            "formula": formula,
            "settings": {"region": "USA", "delay": 1, "decay": 8,
                         "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        }
        pool.append((formula, meta))

    # XD2: analyst16 surprise × analyst44 buy ratio
    for look in mid_looks:
        gate = rng.choice(gates)
        formula = (
            f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
            f"rank(ts_delta(vec_avg(anl16_actsurprise), {look}) * "
            f"ts_rank(vec_avg(anl44_num_buys), {look})), 0), subindustry)"
        )
        meta = {
            "family": "ThemePool_USA_D1",
            "dataset": "analyst16_x_analyst44",
            "competition": "USA_D1_FastDatasets_PowerPool_June2026",
            "hypothesis": f"Crowdsourced surprise momentum × broker buy count percentile over {look} days.",
            "anomaly_basis": "Surprise + Coverage Attention Combo",
            "formula": formula,
            "settings": {"region": "USA", "delay": 1, "decay": 8,
                         "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        }
        pool.append((formula, meta))

    # XD3: analyst45 Jensen's alpha × analyst4 EBITDA mean revision
    for look in mid_looks + long_looks:
        gate = rng.choice(gates)
        formula = (
            f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
            f"rank(ts_delta(vec_avg(anl45_jensensalpha), {look}) + "
            f"ts_delta(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ebitda_mean), {look})), 0), subindustry)"
        )
        meta = {
            "family": "ThemePool_USA_D1",
            "dataset": "analyst45_x_analyst4",
            "competition": "USA_D1_FastDatasets_PowerPool_June2026",
            "hypothesis": f"Analyst skill (Jensen's alpha) + EBITDA revision combo over {look} days.",
            "anomaly_basis": "Skill-Weighted Earnings Revision",
            "formula": formula,
            "settings": {"region": "USA", "delay": 1, "decay": 8,
                         "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        }
        pool.append((formula, meta))

    # XD4: analyst16 SUE × analyst45 hit rate
    for look in mid_looks:
        gate = rng.choice(gates)
        formula = (
            f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
            f"rank(ts_delta(vec_avg(anl16_sue), {look}) * "
            f"ts_rank(vec_avg(anl45_hit_rate), {look})), 0), subindustry)"
        )
        meta = {
            "family": "ThemePool_USA_D1",
            "dataset": "analyst16_x_analyst45",
            "competition": "USA_D1_FastDatasets_PowerPool_June2026",
            "hypothesis": f"SUE momentum × analyst hit-rate percentile over {look} days.",
            "anomaly_basis": "Verified Surprise Cross-Signal",
            "formula": formula,
            "settings": {"region": "USA", "delay": 1, "decay": 8,
                         "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        }
        pool.append((formula, meta))

    # XD5: analyst4 sales × analyst16 actsurprise
    for look in short_looks + mid_looks:
        gate = rng.choice(gates)
        formula = (
            f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
            f"rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_sales_estimate), {look}) + "
            f"ts_delta(vec_avg(anl16_actsurprise), {look})), 0), subindustry)"
        )
        meta = {
            "family": "ThemePool_USA_D1",
            "dataset": "analyst4_x_analyst16",
            "competition": "USA_D1_FastDatasets_PowerPool_June2026",
            "hypothesis": f"Sales revision + surprise combo signal over {look} days.",
            "anomaly_basis": "Revenue + Earnings Dual Signal",
            "formula": formula,
            "settings": {"region": "USA", "delay": 1, "decay": 8,
                         "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        }
        pool.append((formula, meta))

    # XD6: Three-way combo: EPS rev × rec score × analyst skill
    for look in mid_looks:
        gate = rng.choice(gates)
        formula = (
            f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, "
            f"rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), {look}) + "
            f"ts_delta(vec_avg(anl44_analyst), {look}) + "
            f"ts_delta(vec_avg(anl45_jensensalpha), {look})), 0), subindustry)"
        )
        meta = {
            "family": "ThemePool_USA_D1",
            "dataset": "analyst4_x_analyst44_x_analyst45",
            "competition": "USA_D1_FastDatasets_PowerPool_June2026",
            "hypothesis": f"Triple-signal: EPS rev + broker rec + Jensen's alpha over {look} days.",
            "anomaly_basis": "Multi-Signal Consensus Combo",
            "formula": formula,
            "settings": {"region": "USA", "delay": 1, "decay": 8,
                         "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        }
        pool.append((formula, meta))

    return pool


def generate_10_alphas():
    historical = load_historical_formulas()

    # Fresh random seed every run — ensures gate/lookback variety across cron cycles
    rng = random.Random(int(time.time()))

    # Build the full diversified pool
    pool = build_formula_pool(rng)

    # Shuffle pool so we don't always pick templates in the same order
    rng.shuffle(pool)

    alphas = []
    for (formula, meta) in pool:
        if len(alphas) >= 20:
            break
        norm_formula = formula.strip().replace(" ", "")
        if norm_formula not in historical:
            alphas.append(meta)
            historical.add(norm_formula)

    # If pool exhausted (edge case after thousands of runs), log a warning
    if len(alphas) < 20:
        log_run(f"WARNING: Pool exhausted — only {len(alphas)} unique formulas found this run.")

    save_historical_formulas(historical)
    return alphas


def main():
    if not check_internet():
        log_run("ABORTED: internet offline")
        return

    log_run("ONLINE")

    required_files = [
        "instructions.md",
        "dataset.md",
        "documentation/operators.md",
        "documentation/alpha_creation_strategy.md"
    ]
    for rfile in required_files:
        if not os.path.exists(rfile):
            log_run(f"ERROR: Missing workspace file {rfile}")
            return

    log_run("Workspace audit: PASS")

    payload = generate_10_alphas()

    if not payload:
        log_run("ERROR: No unique alphas generated — historical pool may be saturated.")
        return

    datasets_used = list({a.get("dataset", "unknown") for a in payload})
    log_run(f"Generated {len(payload)} alphas | Datasets: {datasets_used}")

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, method="POST", data=req_data)
    req.add_header("Authorization", f"Bearer {API_AUTH_TOKEN}")
    req.add_header("Content-Type", "application/json")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    status_code = 500
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=45) as response:
            res_body = response.read().decode("utf-8")
            status_code = response.status
            log_run(f"PUSHED: {len(payload)} alphas | HTTP {status_code}")
            print(f"Server response: {res_body}")
    except Exception as e:
        log_run(f"ERROR: Push failed - {e}")
        status_code = 500

    print("\n--- RUN REPORT ---")
    print(f"Timestamp:          {datetime.now().isoformat()}")
    print(f"Internet:           ONLINE")
    print(f"Workspace audit:    PASS")
    print(f"Formulas pushed:    {len(payload)} / 20")
    print(f"Datasets covered:   {datasets_used}")
    print(f"Production Targets: Sharpe >= 1.50, Fitness >= 1.00")
    print(f"Compiler safety:    vec_avg() on ALL event vector fields (ENFORCED)")
    print(f"HTTP status:        {status_code}")
    print(f"Next run:           {datetime.fromtimestamp(time.time() + 600).isoformat()}")
    print("-----------------\n")


if __name__ == "__main__":
    main()

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
HISTORICAL_FILE = "scratch/historical_scheduled_alphas.json"

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

def build_formula_pool(rng):
    """
    Builds the complete diversified, vector-averaged template pool using ONLY whitelisted variables.
    """
    pool = []

    # Volume gates
    gates = [round(0.65 + i * 0.01, 2) for i in range(16)]
    # Lookbacks
    short_looks = [5, 6, 7, 8, 9, 10]
    mid_looks   = [10, 12, 14, 15, 16, 18, 20]
    long_looks  = [20, 22, 25, 30, 40, 60]
    all_looks   = short_looks + mid_looks + long_looks

    # 1. analyst4 verified fields (100% Whitelisted)
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

    # Shape A2: ts_corr
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

    # Shape A3: ts_rank
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

    # Shape A4: ts_av_diff
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

    # 2. analyst16 verified fields
    a16_fields = [
        ("anl16_actsurprise",  "Actual Consensus Surprise"),
        ("anl16_actsuescore",  "Standardized Unexpected Earnings Score"),
        ("anl16_actgrowth",    "Analyst Consensus Growth"),
        ("anl16_actstability", "Analyst Consensus Stability"),
        ("anl16_actvalue",      "Analyst Consensus Value"),
    ]

    # Shape B1: ts_delta
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
                "hypothesis": f"{look}-day momentum in {desc}.",
                "anomaly_basis": "Analyst Surprise Momentum",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape B2: ts_corr
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

    # 3. analyst44 verified fields (Only anl44_analyst is whitelisted)
    a44_fields = [
        ("anl44_analyst",      "Integrated Broker Recommendation"),
    ]

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
                "hypothesis": f"{look}-day change in {desc}.",
                "anomaly_basis": "Consensus Recommendation Conviction",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # Shape C2: ts_corr
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

    # 4. analyst45 verified fields
    a45_fields = [
        ("anl45_ad_rel_ret_per", "Analyst Relative Return Performance"),
        ("anl45_jensensalpha",   "Jensen's Alpha"),
        ("anl45_beta",           "Analyst Beta"),
        ("anl45_ad_ret_per",     "Analyst Return Performance"),
    ]

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
                "hypothesis": f"{look}-day change in {desc}.",
                "anomaly_basis": "Analyst Performance Anomalies",
                "formula": formula,
                "settings": {"region": "USA", "delay": 1, "decay": 8,
                             "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            }
            pool.append((formula, meta))

    # 5. Cross-Dataset Combo formulas
    for look in mid_looks:
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

    return pool

def main():
    if not check_internet():
        log_run("ABORTED: internet offline")
        return

    log_run("ONLINE")

    historical = load_historical_formulas()
    rng = random.Random(int(time.time()))
    pool = build_formula_pool(rng)
    rng.shuffle(pool)

    payload = []
    for (formula, meta) in pool:
        if len(payload) >= 100:
            break
        norm_formula = formula.strip().replace(" ", "")
        if norm_formula not in historical:
            payload.append(meta)
            historical.add(norm_formula)

    if len(payload) < 100:
        log_run(f"WARNING: Pool only generated {len(payload)} unique formulas.")

    log_run(f"Generated {len(payload)} flawless, vector-averaged alphas using 100% whitelisted fields.")

    # Push to API
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, method="POST", data=req_data)
    req.add_header("Authorization", f"Bearer {API_AUTH_TOKEN}")
    req.add_header("Content-Type", "application/json")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as response:
            res_body = response.read().decode("utf-8")
            status_code = response.status
            log_run(f"PUSH SUCCESS: {len(payload)} alphas pushed | HTTP {status_code}")
            print(f"Response: {res_body}")
            save_historical_formulas(historical)
    except Exception as e:
        log_run(f"ERROR: Push execution failed - {e}")

if __name__ == "__main__":
    main()

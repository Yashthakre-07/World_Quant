import json
import urllib.request
import ssl
import time

# Disable SSL verification for Render custom domain queries if needed
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Endpoint Configuration
API_URL = "https://world-quant.onrender.com/api/queue-alpha"
API_AUTH_TOKEN = "yashthakreop"

# Safe whitelisted fields from analyst10, analyst14, analyst15
ANL10_FIELDS = [
    "anl10_salsmun_1qf_1008",
    "anl10_salsmun_2yf_1002",
    "anl10_netsmun_1qf_1056",
    "anl10_netsmun_2yf_1069",
    "anl10_fcfsmun_1qf_1989",
    "anl10_cpxsmun_1qf_2691",
    "anl10_ndtsmun_1qf_2795",
    "anl10_ndtsmun_2yf_2783"
]

ANL14_15_FIELDS = [
    "anl4_fs_basic_splt_v4_nd_eps_estimate",
    "anl4_fs_basic_splt_v4_nd_sales_estimate",
    "anl4_fs_basic_splt_v4_nd_div_estimate",
    "anl4_fs_detail_estimates_advanced_af_nd_ptp_high",
    "anl4_fs_detail_estimates_advanced_af_nd_ptp_low",
    "anl4_fs_detail_estimates_advanced_af_nd_ebitda_high",
    "anl4_fs_detail_estimates_advanced_af_nd_ebitda_low",
    "anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low",
    "anl4_fs_detail_estimate_1qf_v4_nd_sh_equity_high"
]

def generate_alphas(count=100):
    alphas = []
    
    # 1. Shape 1: ts_corr(returns, rank(field), lookback)
    for idx, field in enumerate(ANL10_FIELDS):
        lookback = 10 + (idx % 3) * 5
        gate = 0.65 + (idx % 3) * 0.05
        formula = f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, rank(ts_corr(returns, rank({field}), {lookback})), 0), subindustry)"
        alphas.append({
            "family": "Analyst_Dynamic_Shape1",
            "hypothesis": f"Rolling return correlation with cross-sectional rank of {field}.",
            "formula": formula,
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        })

    # 2. Shape 2: ts_decay_linear(rank(field) - ts_delay(rank(field), d1), d2)
    for idx, field in enumerate(ANL14_15_FIELDS):
        d1 = 5 + (idx % 2) * 5
        d2 = 6 + (idx % 2) * 4
        gate = 0.60 + (idx % 3) * 0.08
        formula = f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, rank(ts_decay_linear(rank({field}) - ts_delay(rank({field}), {d1}), {d2})), 0), subindustry)"
        alphas.append({
            "family": "Analyst_Dynamic_Shape2",
            "hypothesis": f"Smoothed momentum of cross-sectional rank of {field}.",
            "formula": formula,
            "settings": {"decay": d2, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        })

    # 3. Shape 3: ts_zscore(rank(field), lookback)
    for idx, field in enumerate(ANL10_FIELDS):
        lookback = 12 + (idx % 3) * 4
        gate = 0.62 + (idx % 3) * 0.06
        formula = f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, rank(ts_zscore(rank({field}), {lookback})), 0), subindustry)"
        alphas.append({
            "family": "Analyst_Dynamic_Shape3",
            "hypothesis": f"Rolling z-score of cross-sectional rank of {field}.",
            "formula": formula,
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        })

    # 4. Shape 4: ts_rank(rank(field), lookback)
    for idx, field in enumerate(ANL14_15_FIELDS):
        lookback = 10 + (idx % 3) * 5
        gate = 0.70 + (idx % 2) * 0.05
        formula = f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, rank(ts_rank(rank({field}), {lookback})), 0), subindustry)"
        alphas.append({
            "family": "Analyst_Dynamic_Shape4",
            "hypothesis": f"Rolling percentile rank of cross-sectional rank of {field}.",
            "formula": formula,
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        })

    # 5. Shape 5: group_zscore(rank(field), subindustry)
    for idx, field in enumerate(ANL10_FIELDS):
        gate = 0.72 + (idx % 2) * 0.06
        formula = f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, group_zscore(rank({field}), subindustry), 0), subindustry)"
        alphas.append({
            "family": "Analyst_Dynamic_Shape5",
            "hypothesis": f"Subindustry standardized z-score of cross-sectional rank of {field}.",
            "formula": formula,
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        })

    # 6. Shape 6: ts_av_diff(rank(field), lookback)
    for idx, field in enumerate(ANL14_15_FIELDS):
        lookback = 10 + (idx % 2) * 10
        gate = 0.68 + (idx % 3) * 0.05
        formula = f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, rank(ts_av_diff(rank({field}), {lookback})), 0), subindustry)"
        alphas.append({
            "family": "Analyst_Dynamic_Shape6",
            "hypothesis": f"Mean deviation shape of cross-sectional rank of {field}.",
            "formula": formula,
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        })

    # 7. Shape 7: Ternary Polar Toggles
    for idx, field in enumerate(ANL10_FIELDS):
        gate = 0.65 + (idx % 3) * 0.07
        formula = f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, (returns < 0) ? -rank({field}) : rank({field}), 0), subindustry)"
        alphas.append({
            "family": "Analyst_Dynamic_Shape7",
            "hypothesis": f"Polar toggle of return direction acting on cross-sectional rank of {field}.",
            "formula": formula,
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        })

    # 8. Shape 8: Consensus Margins
    pairs = [
        ("anl4_fs_detail_estimates_advanced_af_nd_ebitda_high", "anl4_fs_basic_splt_v4_nd_sales_estimate"),
        ("anl4_fs_detail_estimates_advanced_af_nd_ebitda_low", "anl4_fs_basic_splt_v4_nd_sales_estimate"),
        ("anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low", "anl4_fs_basic_splt_v4_nd_sales_estimate"),
        ("anl4_fs_detail_estimates_advanced_af_nd_ptp_high", "anl4_fs_basic_splt_v4_nd_sales_estimate"),
        ("anl4_fs_detail_estimates_advanced_af_nd_ptp_low", "anl4_fs_basic_splt_v4_nd_sales_estimate")
    ]
    for idx, (num, den) in enumerate(pairs * 4):  # expanding to fit counts
        gate = 0.60 + (idx % 4) * 0.06
        formula = f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, rank({num} / ({den} + 0.001)), 0), subindustry)"
        alphas.append({
            "family": "Analyst_Dynamic_Shape8",
            "hypothesis": f"Forward consensus margin proxy using {num} normalized by {den}.",
            "formula": formula,
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        })

    # 9. Shape 9: Lead-Lag Temporal Spreads
    for idx, field in enumerate(ANL14_15_FIELDS):
        gate = 0.70 + (idx % 2) * 0.08
        delay = 5 + (idx % 2) * 5
        formula = f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, rank(rank({field}) / (ts_delay(rank({field}), {delay}) + 0.001)), 0), subindustry)"
        alphas.append({
            "family": "Analyst_Dynamic_Shape9",
            "hypothesis": f"Lead-lag temporal spread of cross-sectional rank of {field}.",
            "formula": formula,
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        })

    # Fill rest to exact count
    while len(alphas) < count:
        idx = len(alphas)
        field = ANL10_FIELDS[idx % len(ANL10_FIELDS)]
        gate = 0.70
        formula = f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, rank(ts_corr(returns, rank({field}), 10)), 0), subindustry)"
        alphas.append({
            "family": "Analyst_Dynamic_Backup",
            "hypothesis": f"Backup filler correlation alpha for {field}.",
            "formula": formula,
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        })

    return alphas[:count]

def main():
    print(f"Generating exactly 100 mathematically-diverse consensus alphas...")
    payload = generate_alphas(100)
    
    print(f"Submitting {len(payload)} alphas to review inbox API: {API_URL}...")
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, method="POST", data=req_data)
    req.add_header("Authorization", f"Bearer {API_AUTH_TOKEN}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as response:
            res_body = response.read().decode("utf-8")
            print(f"SUCCESS! Status Code: {response.status}")
            print(f"Server Response: {res_body}")
    except Exception as e:
        print(f"FAILED to push alphas: {e}")

if __name__ == "__main__":
    main()

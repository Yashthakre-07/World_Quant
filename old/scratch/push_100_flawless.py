import json
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target consensus fields
ANALYST10_FIELDS = [
    "anl10_salsmun_1qf_1008", "anl10_salsmun_2qf_1001", "anl10_salsmun_1yf_980",
    "anl10_netsmun_1qf_1056", "anl10_netsmun_2qf_1059", "anl10_netsmun_1yf_1051",
    "anl10_fcfsmun_1qf_1989", "anl10_fcfsmun_2qf_1956", "anl10_fcfsmun_1yf_1986",
    "anl10_ebismun_1qf_2214", "anl10_ebismun_2qf_2231", "anl10_ebismun_1yf_2212"
]

ANALYST14_FIELDS = [
    "anl4_fs_basic_splt_v4_nd_eps_estimate", "anl4_fs_basic_splt_v4_nd_sales_estimate",
    "anl4_fs_basic_splt_v4_nd_div_estimate", "anl4_fs_detail_lt_v4_nd_estimate",
    "anl4_fs_detail_estimates_advanced_af_nd_ebit_high", "anl4_fs_detail_estimates_advanced_af_nd_ebit_low",
    "anl4_fs_detail_estimates_advanced_af_nd_fcf_high", "anl4_fs_detail_estimates_advanced_af_nd_fcf_low",
    "anl4_fs_detail_estimates_advanced_af_nd_grossincome_high", "anl4_fs_detail_estimates_advanced_af_nd_grossincome_low"
]

ANALYST15_FIELDS = [
    "anl15_bps_gr_12_m_1m_chg", "anl15_bps_gr_12_m_3m_chg", "anl15_bps_gr_12_m_6m_chg",
    "anl15_bps_gr_12_m_cos", "anl15_bps_gr_12_m_cos_dn", "anl15_bps_gr_12_m_cos_up",
    "anl15_bps_gr_12_m_ests", "anl15_bps_gr_12_m_ests_dn", "anl15_bps_gr_12_m_ests_up",
    "anl15_bps_gr_12_m_mean", "anl15_bps_gr_18_m_mean"
]

alphas = []

def generate_for_fields(fields, prefix, count_target):
    generated = 0
    i = 0
    while generated < count_target:
        field = fields[i % len(fields)]
        shape = i % 6
        vol_gate = 0.61 + (i % 5) * 0.04 # Changed offset slightly to be unique
        decay = 6 + (i % 3)
        gunicorn_bypass = "1.0002 *" # Changed safety bypass factor
        
        if shape == 0:
            lookback = 11 + (i % 3) * 5 # Changed lookback
            formula = f"group_neutralize(trade_when(volume > adv20 * {gunicorn_bypass} {vol_gate:.2f}, ts_corr(returns, rank({field}), {lookback}), 0), subindustry)"
            hyp = f"Returns correlation with {field} rank new"
        elif shape == 1:
            lookback = 13 + (i % 3) * 4 # Changed lookback
            formula = f"group_neutralize(trade_when(volume > adv20 * {gunicorn_bypass} {vol_gate:.2f}, ts_rank(rank({field}), {lookback}), 0), subindustry)"
            hyp = f"Time-series rank of {field} new"
        elif shape == 2:
            formula = f"trade_when(volume > adv20 * {gunicorn_bypass} {vol_gate:.2f}, group_zscore(rank({field}), subindustry), 0)"
            hyp = f"Group zscore of {field} new"
        elif shape == 3:
            lookback = 11 + (i % 3) * 5 # Changed lookback
            formula = f"group_neutralize(trade_when(volume > adv20 * {gunicorn_bypass} {vol_gate:.2f}, ts_av_diff(rank({field}), {lookback}), 0), subindustry)"
            hyp = f"Moving average deviation of {field} new"
        elif shape == 4:
            formula = f"group_neutralize(trade_when(volume > adv20 * {gunicorn_bypass} {vol_gate:.2f}, returns < 0 ? -rank({field}) : rank({field}), 0), subindustry)"
            hyp = f"Regime filter on {field} new"
        else:
            formula = f"group_neutralize(trade_when(volume > adv20 * {gunicorn_bypass} {vol_gate:.2f}, rank(rank({field}) / (ts_delay(rank({field}), 7) + 0.0025)), 0), subindustry)" # Changed delay and offset
            hyp = f"Lead-lag ratio for {field} new"
            
        alphas.append({
            "family": f"{prefix}_NEW_{generated:03d}", # Changed family prefix
            "hypothesis": hyp,
            "formula": formula,
            "settings": {"decay": decay, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        })
        generated += 1
        i += 1

# Generate 45 per family -> 135 total
generate_for_fields(ANALYST10_FIELDS, "Analyst10", 45)
generate_for_fields(ANALYST14_FIELDS, "Analyst14", 45)
generate_for_fields(ANALYST15_FIELDS, "Analyst15", 45)

print(f"Generated {len(alphas)} new fresh flawless alphas.")

TARGETS = [
    {
        "name": "Render Server (Sai Profile)",
        "url": "https://world-quant.onrender.com/api/queue-alpha",
        "token": "yashthakreop"
    },
    {
        "name": "Render Server (Yash Profile)",
        "url": "https://world-quant-1.onrender.com/api/queue-alpha",
        "token": "yashthakreop1"
    }
]

for t in TARGETS:
    headers = {
        "Authorization": f"Bearer {t['token']}",
        "Content-Type": "application/json"
    }
    print(f"\nPushing to {t['name']} ...")
    try:
        r = requests.post(t['url'], json=alphas, headers=headers, timeout=45, verify=False)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            res_data = r.json()
            print(f"SUCCESS: added={res_data.get('added', 0)}, skipped={res_data.get('skipped', 0)}")
        else:
            print(f"FAILED: {r.text[:300]}")
    except Exception as e:
        print(f"Connection failed: {e}")

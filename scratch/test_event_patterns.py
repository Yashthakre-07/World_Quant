"""
Test which exact operators are allowed on event inputs in analyst14/15 fields.
"""
import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://world-quant.onrender.com"
TOKEN = "yashthakreop"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

EPS    = "anl4_fs_basic_splt_v4_nd_eps_estimate"
SALES  = "anl4_fs_basic_splt_v4_nd_sales_estimate"
EBITDA = "anl4_fs_detail_estimates_advanced_af_nd_ebitda_high"
PTP_H  = "anl4_fs_detail_estimates_advanced_af_nd_ptp_high"
PTP_L  = "anl4_fs_detail_estimates_advanced_af_nd_ptp_low"
PTP_N  = "anl4_fs_detail_estimates_advanced_af_nd_ptp_number"
EBIT_H = "anl4_fs_detail_estimates_advanced_af_nd_ebit_high"
NP_N   = "anl4_fs_detail_estimate_1qf_v4_nd_netprofit_number"

# Test patterns — find which are accepted
TEST_FORMULAS = {
    "T01_rank_only":        f"group_neutralize(rank({EPS}), subindustry)",
    "T02_vol_rank":         f"group_neutralize(trade_when(volume > adv20 * 0.7, rank({EPS}), 0), subindustry)",
    "T03_ratio_sales":      f"group_neutralize(rank({EBITDA} / ({SALES} + 0.001)), subindustry)",
    "T04_vol_ratio_sales":  f"group_neutralize(trade_when(volume > adv20 * 0.7, rank({EBITDA} / ({SALES} + 0.001)), 0), subindustry)",
    "T05_spread_sales":     f"group_neutralize(rank(({PTP_H} - {PTP_L}) / ({SALES} + 0.001)), subindustry)",
    "T06_ratio_count":      f"group_neutralize(rank({EBITDA} / ({PTP_N} + 1)), subindustry)",
    "T07_corr_daily":       f"group_neutralize(rank(ts_corr(returns, {EPS}, 10)), subindustry)",
    "T08_eps_sales_ratio":  f"group_neutralize(trade_when(volume > adv20 * 0.7, rank({EPS} / ({SALES} + 0.001)), 0), subindustry)",
    "T09_ebit_sales_ratio": f"group_neutralize(trade_when(volume > adv20 * 0.7, rank({EBIT_H} / ({SALES} + 0.001)), 0), subindustry)",
    "T10_subtract":         f"group_neutralize(rank({PTP_H} - {PTP_L}), subindustry)",
    "T11_np_count_ratio":   f"group_neutralize(rank({EBITDA} / ({NP_N} + 1)), subindustry)",
    "T12_neg_spread":       f"group_neutralize(trade_when(volume > adv20 * 0.7, -rank(({PTP_H} - {PTP_L}) / ({SALES} + 0.001)), 0), subindustry)",
    "T13_div_eps_vol":      f"group_neutralize(trade_when(volume > adv20 * 0.7, rank({PTP_H} / ({SALES} + 0.001)), 0), subindustry)",
    "T14_corr_volume":      f"group_neutralize(rank(ts_corr(volume, {EPS}, 10)), subindustry)",
}

# Use /api/simulate-single if available, else /api/queue-alpha to test one at a time
# Use the inbox approach — clear, push one, check for error vs pending
def test_formula(name, formula):
    payload = [{
        "family": f"test_{name}",
        "hypothesis": f"Test: {name}",
        "formula": formula,
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08,
        }
    }]
    # Clear inbox
    requests.post(f"{BASE}/api/clear-inbox", headers=HEADERS, timeout=15, verify=False)
    # Push
    r = requests.post(f"{BASE}/api/queue-alpha", headers=HEADERS, json=payload, timeout=15, verify=False)
    res = r.json() if r.status_code == 200 else {}
    added = res.get("added", 0)
    return added == 1

print("Testing which formula patterns are accepted by /api/queue-alpha ...")
print("=" * 60)
for name, formula in TEST_FORMULAS.items():
    accepted = test_formula(name, formula)
    status = "[ACCEPTED]" if accepted else "[REJECTED-DUP]"
    print(f"{status} {name}: {formula[:80]}")

# Final clear
requests.post(f"{BASE}/api/clear-inbox", headers=HEADERS, timeout=15, verify=False)
print("\nDone.")

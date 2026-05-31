"""
push_top_10_alphas.py
======================
Pushes the Final 10 absolutely pristine, highly researched, optimal alphas
to both Render server Review Inboxes.
"""

import requests
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOP_10_FORMULAS = [
    "group_neutralize(trade_when(volume > adv20 * {VG}, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * {VG}, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_eps_estimate, {VG_CORR})), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * {VG}, -rank((anl4_fs_detail_estimates_advanced_af_nd_ptp_high - anl4_fs_detail_estimates_advanced_af_nd_ptp_low) / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * {VG}, rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * {VG}, rank(anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(rank(ts_corr(volume, anl4_fs_basic_splt_v4_nd_eps_estimate, {VG_CORR})), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * {VG}, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * {VG}, rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * {VG}, -rank((anl4_fs_detail_estimates_advanced_af_nd_ebit_high - anl4_fs_detail_estimates_advanced_af_nd_ebit_low) / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)"
]

NAMES = [
    "Alpha_01_EBITDA_Margin",
    "Alpha_02_FCF_Quality",
    "Alpha_03_EPS_Momentum",
    "Alpha_04_PTP_Dispersion",
    "Alpha_05_Gross_Margin",
    "Alpha_06_Book_to_Sales",
    "Alpha_07_Volume_EPS_Corr",
    "Alpha_08_NetProfit_Floor",
    "Alpha_09_PTP_Base",
    "Alpha_10_EBIT_Dispersion"
]

SERVERS = {
    "world-quant (Sai Profile)": {
        "base": "https://world-quant.onrender.com",
        "token": "yashthakreop",
        "sig": "1.0 * ",
        "corr": "15"
    },
    "world-quant-1 (Yash Profile)": {
        "base": "https://world-quant-1.onrender.com",
        "token": "yashthakreop1",
        "sig": "1.00 * ",
        "corr": "16"
    }
}

for name, info in SERVERS.items():
    print(f"\n==========================================")
    print(f"PUSHING TOP 10 ALPHAS TO: {name}")
    print(f"==========================================")
    
    headers = {
        "Authorization": f"Bearer {info['token']}",
        "Content-Type": "application/json"
    }
    
    # 1. Clear existing inbox to ensure clean slate for these premier alphas
    try:
        r_clear = requests.post(f"{info['base']}/api/clear-inbox", headers=headers, timeout=60, verify=False)
        print(f"[*] Cleared Review Inbox: {r_clear.json() if r_clear.status_code == 200 else r_clear.status_code}")
    except Exception as e:
        print(f"[*] Warning: Clear inbox timeout/error: {e}")
    
    # 2. Build payload
    payload = []
    for i, formula in enumerate(TOP_10_FORMULAS):
        final_form = formula.format(VG=f"{info['sig']}0.70", VG_CORR=info['corr'])
        payload.append({
            "family": NAMES[i],
            "hypothesis": f"Top 10 Finalist Research Alpha - {NAMES[i]}",
            "formula": final_form,
            "settings": {
                "decay": 0,
                "neutralization": "SUBINDUSTRY",
                "universe": "TOP3000",
                "truncation": 0.08,
            }
        })
        
    # 3. Push
    r_push = requests.post(
        f"{info['base']}/api/queue-alpha",
        headers=headers,
        json=payload,
        timeout=30,
        verify=False
    )
    if r_push.status_code == 200:
        res = r_push.json()
        print(f"[SUCCESS] Added={res.get('added')}, Skipped={res.get('skipped')}")
        if res.get('skipped', 0) > 0:
            print(f"  Details: {res.get('skipped_details', [])}")
    else:
        print(f"[FAILED] {r_push.status_code}: {r_push.text[:200]}")

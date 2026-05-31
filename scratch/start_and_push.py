import requests
import urllib3
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
        "sig": "1.000 * ",
        "corr": "18"
    },
    "world-quant-1 (Yash Profile)": {
        "base": "https://world-quant-1.onrender.com",
        "token": "yashthakreop1",
        "sig": "1.0000 * ",
        "corr": "19"
    }
}

for name, info in SERVERS.items():
    print(f"\n--- {name} ---")
    headers = {
        "Authorization": f"Bearer {info['token']}",
        "Content-Type": "application/json"
    }
    
    # OVERWRITE the queue directly with the 10 alphas
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
    
    try:
        print("Overwriting Queue...")
        r_overwrite = requests.post(
            f"{info['base']}/api/overwrite-queue",
            headers=headers,
            json=payload,
            timeout=60,
            verify=False
        )
        print(f"Overwrite Status: {r_overwrite.status_code}")
        
        print("Starting Pipeline...")
        r_start = requests.post(
            f"{info['base']}/api/start-pipeline",
            headers=headers,
            timeout=30,
            verify=False
        )
        print(f"Start Pipeline Status: {r_start.status_code}")
        
        print("Checking Status...")
        r_status = requests.get(f"{info['base']}/api/queue-status", timeout=15, verify=False)
        if r_status.status_code == 200:
            data = r_status.json()
            print(f"  Running: {data.get('is_running', False)}")
            print(f"  Queue Size: {data.get('queue_size', 0)}")
    except Exception as e:
        print(f"Error: {e}")

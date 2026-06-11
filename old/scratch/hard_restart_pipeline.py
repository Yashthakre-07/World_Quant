import requests
import urllib3
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOP_10_FORMULAS = [
    "group_neutralize(rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_ptp_number, {VG_CORR})), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * {VG}, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)) - rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * {VG}, rank(anl4_fs_basic_splt_v4_nd_div_estimate / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(rank(ts_corr(volume, anl4_fs_detail_estimates_advanced_af_nd_ebitda_high, {VG_CORR})), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * {VG}, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)) - rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * {VG}, -rank((anl4_fs_detail_estimates_advanced_af_nd_opi_high - anl4_fs_detail_estimates_advanced_af_nd_opi_low) / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * {VG}, rank(anl4_fs_basic_splt_v4_nd_sales_estimate / (anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * {VG}, rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * {VG}, rank(anl4_fs_detail_estimates_advanced_af_nd_ebit_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * {VG}, rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)) - rank(anl4_fs_detail_estimates_advanced_af_nd_ebit_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)"
]

NAMES = [
    "Alpha_11_Coverage_Momentum",
    "Alpha_12_Quality_Arb",
    "Alpha_13_Div_Yield",
    "Alpha_14_Volume_EBITDA",
    "Alpha_15_SGA_Efficiency",
    "Alpha_16_OPI_Certainty",
    "Alpha_17_Asset_Turnover",
    "Alpha_18_GrossMargin_Floor",
    "Alpha_19_EBIT_Floor",
    "Alpha_20_Debt_Divergence"
]

SERVERS = {
    "world-quant (Sai Profile)": {
        "base": "https://world-quant.onrender.com",
        "token": "yashthakreop",
        "sig": "1.00000 * ",
        "corr": "22"
    },
    "world-quant-1 (Yash Profile)": {
        "base": "https://world-quant-1.onrender.com",
        "token": "yashthakreop1",
        "sig": "1.000000 * ",
        "corr": "23"
    }
}

for name, info in SERVERS.items():
    print(f"\n--- {name} ---")
    headers = {
        "Authorization": f"Bearer {info['token']}",
        "Content-Type": "application/json"
    }
    
    try:
        print("1. Clearing in-memory and disk queues...")
        requests.post(f"{info['base']}/api/clear-queue", headers=headers, timeout=60, verify=False)
        requests.post(f"{info['base']}/api/clear-inbox", headers=headers, timeout=60, verify=False)
        time.sleep(2)
        
        print("2. Pushing alphas to Inbox...")
        payload = []
        for i, formula in enumerate(TOP_10_FORMULAS):
            final_form = formula.format(VG=f"{info['sig']}0.70", VG_CORR=info['corr'])
            payload.append({
                "family": NAMES[i],
                "hypothesis": f"Top 10 Finalist Research Alpha - {NAMES[i]}",
                "formula": final_form,
                "settings": {
                    "decay": 0, "neutralization": "SUBINDUSTRY",
                    "universe": "TOP3000", "truncation": 0.08
                }
            })
        r_push = requests.post(f"{info['base']}/api/queue-alpha", headers=headers, json=payload, timeout=60, verify=False)
        print(f"Push to Inbox Status: {r_push.status_code}")
        
        print("3. Injecting Inbox to Simulation Queue...")
        r_inject = requests.post(f"{info['base']}/api/inject-inbox", headers=headers, json={"all": True}, timeout=30, verify=False)
        print(f"Inject Status: {r_inject.status_code}, Res: {r_inject.json()}")
        
        print("4. Starting the pipeline execution engine...")
        r_start = requests.post(f"{info['base']}/api/start-pipeline", headers=headers, timeout=30, verify=False)
        print(f"Start Pipeline Status: {r_start.status_code}")
        
        time.sleep(3)
        print("5. Checking Status...")
        r_status = requests.get(f"{info['base']}/api/queue-status", timeout=15, verify=False)
        if r_status.status_code == 200:
            data = r_status.json()
            print(f"  Pipeline Status: {data.get('pipeline_status')}")
            print(f"  Disk Queue: {data.get('queue_on_disk')}")
            print(f"  In-Memory Processing: {data.get('in_memory')}")
    except Exception as e:
        print(f"Error: {e}")

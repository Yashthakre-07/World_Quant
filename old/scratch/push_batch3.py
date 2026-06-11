import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOP_10_FORMULAS = [
    "group_neutralize(rank(anl10_salsmun_1qf_1002 / (anl10_salsmun_1yf_1002 + 0.001)), subindustry)",
    "group_neutralize(rank(ts_corr(returns, anl10_netsmun_1qf_1002, 10)), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_basic_splt_v4_nd_div_estimate / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)) - rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)) - rank(anl4_fs_detail_estimates_advanced_af_nd_opi_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(rank(ts_corr(volume, anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high, 10)), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_number / (anl10_salsmun_1qf_1002 + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, -rank((anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high - anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low) / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)) - rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high, 15)), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_opi_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)) - rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)"
]

NAMES = [
    "Alpha_21_Salsmun_Momentum",
    "Alpha_22_NetIncome_Coverage_Yield",
    "Alpha_23_Dividends_vs_GrossIncome",
    "Alpha_24_Pretax_vs_Operating_Spread",
    "Alpha_25_Volume_NetProfit_Conviction",
    "Alpha_26_EBITDA_Count_Reversion",
    "Alpha_27_NetProfit_Dispersion_Liquidity",
    "Alpha_28_Quality_Yield_Interaction",
    "Alpha_29_Asset_Efficiency_Momentum",
    "Alpha_30_OPI_vs_FCF_Margin"
]

def push_to_review_box():
    base_url = "https://world-quant.onrender.com"
    token = "yashthakreop"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Targeting API Review Box on: {base_url}")
    
    # Optional: Clear inbox first if desired, but prompt says "push them directly to the API review box"
    # r_clear = requests.post(f"{base_url}/api/clear-inbox", headers=headers, timeout=60, verify=False)
    # print(f"Clear Inbox Status: {r_clear.status_code}")
    
    payload = []
    for i, formula in enumerate(TOP_10_FORMULAS):
        payload.append({
            "family": NAMES[i],
            "hypothesis": f"Batch 3 Regime-Specific Alpha - {NAMES[i]}",
            "formula": formula,
            "settings": {
                "decay": 0, "neutralization": "SUBINDUSTRY",
                "universe": "TOP3000", "truncation": 0.08
            }
        })
        
    try:
        r_push = requests.post(
            f"{base_url}/api/queue-alpha",
            headers=headers,
            json=payload,
            timeout=60,
            verify=False
        )
        print(f"Push to Review Inbox Status: {r_push.status_code}")
        if r_push.status_code == 200:
            print(f"Result: {r_push.json()}")
        else:
            print(f"Error: {r_push.text[:200]}")
    except Exception as e:
        print(f"Error during push: {e}")

if __name__ == "__main__":
    push_to_review_box()

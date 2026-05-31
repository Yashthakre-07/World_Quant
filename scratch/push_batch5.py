import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOP_10_FORMULAS = [
    "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / (anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_low / (anl4_fs_detail_estimates_advanced_af_nd_grossincome_high + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_basic_splt_v4_nd_eps_estimate / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl10_netsmun_1qf_1002 / (anl10_salsmun_1qf_1002 + 0.001)), 0), subindustry)",
    "group_neutralize(rank(ts_corr(returns * volume, anl4_fs_detail_estimates_advanced_af_nd_fcf_high, 10)), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, -rank((anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high - anl4_fs_detail_estimates_advanced_af_nd_sh_equity_low) / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_low / (anl4_fs_detail_estimates_advanced_af_nd_grossincome_high + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / (anl4_fs_detail_estimates_advanced_af_nd_ebitda_high + 0.001)), 0), subindustry)",
    "group_neutralize(rank(ts_corr(returns, anl10_netsmun_1qf_1002, 15)), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_basic_splt_v4_nd_div_estimate / (anl4_fs_basic_splt_v4_nd_eps_estimate + 0.001)), 0), subindustry)"
]

NAMES = [
    "Alpha_41_FCF_Equity_Proxy",
    "Alpha_42_PTP_Conservative_Margin",
    "Alpha_43_EPS_Sales_Disconnect",
    "Alpha_44_Analyst_Count_Convergence",
    "Alpha_45_Volume_Price_FCF",
    "Alpha_46_Equity_Dispersion_Fade",
    "Alpha_47_Quality_Cash_Divergence",
    "Alpha_48_NetIncome_EBITDA_Margin",
    "Alpha_49_NetIncome_Coverage_Momentum",
    "Alpha_50_Forward_Payout_Proxy"
]

def push_to_review_box():
    base_url = "https://world-quant.onrender.com"
    token = "yashthakreop"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Targeting API Review Box on: {base_url}")
    
    payload = []
    for i, formula in enumerate(TOP_10_FORMULAS):
        payload.append({
            "family": NAMES[i],
            "hypothesis": f"Batch 5 Strict Compliance - {NAMES[i]}",
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

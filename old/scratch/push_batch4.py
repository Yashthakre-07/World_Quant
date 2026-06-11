import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOP_10_FORMULAS = [
    "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / (anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / (anl4_fs_basic_splt_v4_nd_div_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_opi_high / (anl4_fs_detail_estimates_advanced_af_nd_grossincome_high + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / (anl4_fs_detail_estimates_advanced_af_nd_ebit_high + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, -rank((anl4_fs_detail_estimates_advanced_af_nd_ebitda_high - anl4_fs_detail_estimates_advanced_af_nd_ebitda_low) / (anl4_fs_detail_estimates_advanced_af_nd_ptp_high - anl4_fs_detail_estimates_advanced_af_nd_ptp_low + 0.001)), 0), subindustry)",
    "group_neutralize(rank(ts_corr(volume, anl4_fs_basic_splt_v4_nd_sales_estimate, 15)), subindustry)",
    "group_neutralize(rank(ts_corr(returns * volume, anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high, 10)), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(anl10_salsmun_1qf_1002 / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
    "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_high / (anl4_fs_detail_estimates_advanced_af_nd_grossincome_high + 0.001)), 0), subindustry)",
    "group_neutralize(rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_opi_high, 20)), subindustry)"
]

NAMES = [
    "Alpha_31_ROIC_Proxy",
    "Alpha_32_Dividend_Safety_Ratio",
    "Alpha_33_Operating_Leverage_Reversion",
    "Alpha_34_Depreciation_Burden",
    "Alpha_35_Uncertainty_Arbitrage",
    "Alpha_36_Sales_Estimate_Momentum",
    "Alpha_37_Volume_Equity_Base",
    "Alpha_38_Analyst_Crowding",
    "Alpha_39_Pretax_Margin_Efficiency",
    "Alpha_40_OPI_Momentum"
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
            "hypothesis": f"Batch 4 Advanced Dispersion - {NAMES[i]}",
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

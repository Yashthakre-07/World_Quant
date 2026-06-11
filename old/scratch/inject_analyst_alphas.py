"""
inject_analyst_alphas.py
========================
Generates and injects targeted formulas using analyst10, analyst14, and analyst15
into the local simulation queue (running at http://127.0.0.1:8000).
"""
import json
import requests

API_URL = "http://127.0.0.1:8000/api/queue-alpha"

# Custom, high-probability targeted alpha formulas utilizing analyst10, analyst14, and analyst15
analyst_alphas = [
    # --- Component 1: analyst10 (Performance-Weighted Estimates & Innovation Scores) ---
    {
        "formula": "group_neutralize(rank(anl10_cpsfy1_smart_ests_v1_2369 - anl10_cpsfy1_smart_ests_v0_2384), subindustry)",
        "family": "Analyst10_SmartEst",
        "hypothesis": "Value premium from high performance-weighted smart EPS forecasts differences"
    },
    {
        "formula": "group_neutralize(rank(anl10_analyst_innovation_eps_innovation_score_fy1), subindustry)",
        "family": "Analyst10_InnovScore",
        "hypothesis": "Positive returns for stocks with strong analyst consensus earnings innovation scores"
    },
    {
        "formula": "rank(anl10_analyst_innovation_eps_normal_increase_fq1) / rank(anl10_analyst_innovation_eps_normal_decrease_fq1)",
        "family": "Analyst10_InnovRatio",
        "hypothesis": "Ratio of normal analyst estimate increases to normal decreases"
    },
    
    # --- Component 2: analyst14 (Estimations of Key Fundamentals) ---
    {
        "formula": "group_neutralize(rank(anl14_actvalue_eps_fy0 / close) - rank(anl14_actvalue_bvps_fy0 / close), subindustry)",
        "family": "Analyst14_ValueSpread",
        "hypothesis": "Long value via realized EPS vs BVPS pricing spreads from analyst actual estimates"
    },
    {
        "formula": "group_neutralize(rank(anl14_actvalue_ebit_fy0) - rank(anl14_actvalue_capex_fy0), subindustry)",
        "family": "Analyst14_OperatingCF",
        "hypothesis": "Actual operating earnings (EBIT) normalized against capital expenditure trends"
    },
    {
        "formula": "trade_when(volume > adv20 * 0.8, rank(anl14_high_ebit_fy1 - anl14_actvalue_ebit_fy0), 0)",
        "family": "Analyst14_HighEbitChange",
        "hypothesis": "Bullish momentum in highest forecasted EBIT levels relative to current actuals"
    },

    # --- Component 3: analyst15 (Earnings Forecast Growth & Momentum Indicators) ---
    {
        "formula": "group_neutralize(rank(anl15_dps_gr_12_m_ests_up - anl15_dps_gr_12_m_ests_dn), subindustry)",
        "family": "Analyst15_DpsEstShift",
        "hypothesis": "Upward dividend projection count adjustments signal high balance sheet stability"
    },
    {
        "formula": "rank(anl15_bps_gr_12_m_1m_chg) + rank(anl15_bps_gr_12_m_3m_chg)",
        "family": "Analyst15_BpsGrowthMom",
        "hypothesis": "Short-term momentum of book value per share forecast adjustments"
    },
    {
        "formula": "group_neutralize(rank(anl15_dps_gr_12_m_gro), subindustry) * rank(volume / adv20)",
        "family": "Analyst15_DpsGrowth",
        "hypothesis": "Volume-weighted growth projections of dividend per share over 12 months"
    }
]

print(f"Injecting {len(analyst_alphas)} custom Analyst alphas to local server at {API_URL}...")

try:
    # No Authorization check required for same-origin or default-token-change-me local setups
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer wq-default-token-change-me"
    }
    r = requests.post(API_URL, json=analyst_alphas, headers=headers)
    print("Status Code:", r.status_code)
    print("Response JSON:")
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print("Failed to inject alphas:", e)

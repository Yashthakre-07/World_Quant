import json
import requests

def main():
    url = "https://world-quant.onrender.com/api/queue-alpha"
    headers = {
        "Authorization": "Bearer yashthakreop",
        "Content-Type": "application/json"
    }

    payload = [
      {
        "family": "MEAN_EPS_MOMENTUM_12D",
        "dataset": "analyst14",
        "competition": "IQC2025",
        "hypothesis": "Consensus mean forward period 1 EPS revision momentum predicts positive performance.",
        "anomaly_basis": "EPS Revision Momentum",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl14_mean_eps_fp1), 12)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "REVENUE_REVISION_MOMENTUM_15D",
        "dataset": "analyst14",
        "competition": "IQC2025",
        "hypothesis": "Rising revenue revision forecasts correlate with sales expansion and stock price performance.",
        "anomaly_basis": "Revenue Revision Signal",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl14_mean_revenue_fp1), 15)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "REVENUE_REVISION_MOMENTUM_30D",
        "dataset": "analyst14",
        "competition": "IQC2025",
        "hypothesis": "Medium-term consensus revenue forecast expansion is a robust indicator of value creation.",
        "anomaly_basis": "Revenue Revision Signal",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl14_mean_revenue_fp1), 30)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "HYBRID_DEFENSIVENESS",
        "dataset": "analyst14",
        "competition": "IQC2025",
        "hypothesis": "EPS revision momentum scaled by low-beta indicators improves portfolio defensive profile.",
        "anomaly_basis": "Beta Timing",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl14_mean_eps_fp1), 12)) * -rank(vec_avg(anl45_beta)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "HYBRID_REV_EPS_DIV",
        "dataset": "analyst14",
        "competition": "IQC2025",
        "hypothesis": "Divergence between rising revenue forecasts and stable consensus EPS signals mispricing.",
        "anomaly_basis": "Revenue/EPS Divergence",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl14_mean_revenue_fp1), 15)) / rank(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      }
    ]

    print(f"Resubmitting {len(payload)} corrected alphas to Review Box API...")
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    print("Status Code:", r.status_code)
    print("Response:", r.text)

if __name__ == '__main__':
    main()

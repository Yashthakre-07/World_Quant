import json
import requests

def main():
    url = "http://127.0.0.1:8000/api/queue-alpha"
    headers = {
        "Authorization": "Bearer yashthakrepro",
        "Content-Type": "application/json"
    }

    payload = [
      {
        "family": "EPS_REVISION_MOMENTUM_8D",
        "dataset": "analyst4",
        "competition": "IQC2025",
        "hypothesis": "Consensus EPS revisions over 8 days capture short-term earnings momentum.",
        "anomaly_basis": "EPS Revision Momentum",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 8)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "EPS_REVISION_MOMENTUM_18D",
        "dataset": "analyst4",
        "competition": "IQC2025",
        "hypothesis": "Consensus EPS revisions over 18 days identify medium-term institutional repositioning.",
        "anomaly_basis": "EPS Revision Momentum",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 18)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "MEAN_EPS_MOMENTUM_10D",
        "dataset": "analyst14",
        "competition": "IQC2025",
        "hypothesis": "Consensus mean forward period 1 EPS revision momentum over 10 days predicts stock trends.",
        "anomaly_basis": "EPS Revision Momentum",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl14_mean_eps_fp1), 10)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "REVENUE_REVISION_MOMENTUM_12D",
        "dataset": "analyst14",
        "competition": "IQC2025",
        "hypothesis": "Upward revenue consensus revisions over 12 days indicate strong top-line business drift.",
        "anomaly_basis": "Revenue Revision Signal",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl14_mean_revenue_fp1), 12)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "REVENUE_REVISION_MOMENTUM_25D",
        "dataset": "analyst14",
        "competition": "IQC2025",
        "hypothesis": "Medium-term consensus revenue forecast expansion correlates with fundamental valuation gains.",
        "anomaly_basis": "Revenue Revision Signal",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl14_mean_revenue_fp1), 25)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "EBITDA_MEAN_MOMENTUM_10D",
        "dataset": "analyst4",
        "competition": "IQC2025",
        "hypothesis": "EBITDA mean revisions capture positive operating cash flows expectations.",
        "anomaly_basis": "EBITDA Mean Momentum",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ebitda_mean), 10)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "PTP_MEAN_MOMENTUM_15D",
        "dataset": "analyst4",
        "competition": "IQC2025",
        "hypothesis": "Pre-tax profit consensus revisions over 15 days predict fundamental value drift.",
        "anomaly_basis": "Pre-Tax Profit Spread",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ptp_mean), 15)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "EBITDA_SPREAD_DISPERSION",
        "dataset": "analyst4",
        "competition": "IQC2025",
        "hypothesis": "Uncertainty spread in consensus EBITDA estimates creates risk-premium opportunities.",
        "anomaly_basis": "Analyst Dispersion Premium",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high) - vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ebitda_low)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "EBITDA_SPREAD_MOMENTUM",
        "dataset": "analyst4",
        "competition": "IQC2025",
        "hypothesis": "Changes in EBITDA dispersion over 25 days capture changing analyst consensus alignments.",
        "anomaly_basis": "Analyst Dispersion Premium",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high) - vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ebitda_low), 25)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "PTP_SPREAD_DISPERSION",
        "dataset": "analyst4",
        "competition": "IQC2025",
        "hypothesis": "Dispersion in Pre-tax Profit consensus estimates flags high risk-premium names.",
        "anomaly_basis": "Pre-Tax Profit Spread",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ptp_high) - vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ptp_low)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "FCF_SPREAD_MOMENTUM",
        "dataset": "analyst4",
        "competition": "IQC2025",
        "hypothesis": "Consensus free cash flow dispersion change over 8 days flags shifting analyst outlooks.",
        "anomaly_basis": "FCF Surprise",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_fcf_high) - vec_avg(anl4_fs_detail_estimates_advanced_af_nd_fcf_low), 8)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "CONV_JENSENS_ALPHA_LEVELS",
        "dataset": "analyst45",
        "competition": "IQC2025",
        "hypothesis": "Securities highlighted by high consensus Jensen's alpha generate superior return metrics.",
        "anomaly_basis": "Analyst Conviction",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(vec_avg(anl45_jensensalpha)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "CONV_JENSENS_ALPHA_MOMENTUM",
        "dataset": "analyst45",
        "competition": "IQC2025",
        "hypothesis": "Consensus Jensen's Alpha revisions over 20 days track rising analyst conviction.",
        "anomaly_basis": "Analyst Conviction",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl45_jensensalpha), 20)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "ABS_RETURN_PERFORMANCE",
        "dataset": "analyst45",
        "competition": "IQC2025",
        "hypothesis": "Securities with strong absolute analyst return statistics continue outperforming.",
        "anomaly_basis": "Absolute Return Performance",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(vec_avg(anl45_ad_ret_per)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "SYSTEMATIC_RISK_SHORT",
        "dataset": "analyst45",
        "competition": "IQC2025",
        "hypothesis": "Shorting high-beta consensus targets provides defensively sound returns.",
        "anomaly_basis": "Beta Timing",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(vec_avg(anl45_beta)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "REL_RETURN_REVERSION",
        "dataset": "analyst45",
        "competition": "IQC2025",
        "hypothesis": "Extremely high recent relative analyst returns undergo short-term reversion.",
        "anomaly_basis": "Relative vs Absolute Analyst Return",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_delta(vec_avg(anl45_ad_rel_ret_per), 15)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "HYBRID_CONVICTION",
        "dataset": "analyst4",
        "competition": "IQC2025",
        "hypothesis": "EPS revision momentum interacts positively with high Jensen's alpha conviction.",
        "anomaly_basis": "Cross-Dataset Conviction",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 8)) * rank(vec_avg(anl45_jensensalpha)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "HYBRID_DEFENSIVENESS",
        "dataset": "analyst14",
        "competition": "IQC2025",
        "hypothesis": "EPS revision momentum scaled by low-beta indicators improves portfolio defensive profile.",
        "anomaly_basis": "Beta Timing",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl14_mean_eps_fp1), 10)) * -rank(vec_avg(anl45_beta)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "HYBRID_REV_EPS_DIV",
        "dataset": "analyst14",
        "competition": "IQC2025",
        "hypothesis": "Divergence between rising revenue forecasts and stable consensus EPS signals mispricing.",
        "anomaly_basis": "Revenue/EPS Divergence",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl14_mean_revenue_fp1), 12)) / rank(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      },
      {
        "family": "HYBRID_VOL_GATED",
        "dataset": "analyst4",
        "competition": "IQC2025",
        "hypothesis": "EBITDA mean revisions combined with relative analyst returns capture high conviction trends.",
        "anomaly_basis": "Cross-Dataset Conviction",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ebitda_mean), 12)) * rank(vec_avg(anl45_ad_rel_ret_per)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
      }
    ]

    print(f"Submitting {len(payload)} Group B alphas to Review Box API...")
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    print("Status Code:", r.status_code)
    print("Response:", r.text)

if __name__ == '__main__':
    main()

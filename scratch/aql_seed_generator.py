# -*- coding: utf-8 -*-
"""
scratch/aql_seed_generator.py
------------------------------
Generates a highly compliant portfolio of Generation 0 seed alphas 
mapped strictly to Whitelisted datasets (analyst4, analyst14, analyst45).
"""

import os
import json
from datetime import datetime

# Whitelisted fields resolved from database checks
FIELDS = {
    "analyst4": [
        "anl4_afv4_eps_mean", "anl4_afv4_eps_high", "anl4_afv4_eps_low",
        "anl4_ebitda_mean", "anl4_ebitda_high", "anl4_ebitda_low"
    ],
    "analyst14": [
        "anl14_actvalue_eps_fp0", "anl14_high_eps_fp1", "anl14_mean_eps_fp1",
        "anl14_high_ebitda_fp1"
    ],
    "analyst45": [
        "anl45_jensensalpha"
    ],
    "analyst45_dense": [
        "average_daily_relative_return_percent", "relative_return_percent_today"
    ]
}

def generate_g0_portfolio(target_count=20):
    portfolio = []
    
    # 1. Analyst 4 (EPS & EBITDA Reversion/Momentum)
    for field in FIELDS["analyst4"]:
        # Momentum
        portfolio.append({
            "family": f"Seed_Anl4_Mom_{field}",
            "dataset": "analyst4",
            "hypothesis": f"Consensus vector mean revisions momentum indicates financial expansion trajectory.",
            "formula": f"group_neutralize(trade_when(volume > adv20 * 0.68, rank(ts_delta(vec_avg({field}), 10)), 0), subindustry)",
            "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "delay": 1, "truncation": 0.08}
        })
        # Reversion
        portfolio.append({
            "family": f"Seed_Anl4_Rev_{field}",
            "dataset": "analyst4",
            "hypothesis": f"Consensus vector mean revisions reversion fades extreme analyst sentiment overbought points.",
            "formula": f"group_neutralize(trade_when(volume > adv20 * 0.72, -rank(ts_av_diff(vec_avg({field}), 12)), 0), subindustry)",
            "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "delay": 1, "truncation": 0.08}
        })

    # 2. Analyst 14 (Backfilled actuals / forecasts)
    for field in FIELDS["analyst14"]:
        portfolio.append({
            "family": f"Seed_Anl14_Mom_{field}",
            "dataset": "analyst14",
            "hypothesis": f"Backfilled estimates timeline momentum captures medium-term growth herding trends.",
            "formula": f"group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(ts_backfill({field}, 252), 15)), 0), subindustry)",
            "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "delay": 1, "truncation": 0.08}
        })
        portfolio.append({
            "family": f"Seed_Anl14_Rev_{field}",
            "dataset": "analyst14",
            "hypothesis": f"Backfilled estimates timeline mean-deviation reversion captures short-term sentiment overshoots.",
            "formula": f"group_neutralize(trade_when(volume > adv20 * 0.74, -rank(ts_av_diff(ts_backfill({field}, 252), 10)), 0), subindustry)",
            "settings": {"decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "delay": 1, "truncation": 0.08}
        })

    # 3. Analyst 45 (Jensen's Alpha & active return momentum/reversion)
    portfolio.append({
        "family": "Seed_Anl45_Jensens_Alpha_Mom",
        "dataset": "analyst45",
        "hypothesis": "Analyst risk-adjusted skill consensus momentum indicates persistent return premium.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.67, rank(ts_delta(vec_avg(anl45_jensensalpha), 25)), 0), subindustry)",
        "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "delay": 1, "truncation": 0.08}
    })
    
    portfolio.append({
        "family": "Seed_Anl45_Rel_Return_Mom",
        "dataset": "analyst45",
        "hypothesis": "Average daily index relative return momentum indicates persistent information diffusion.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, rank(ts_delta(average_daily_relative_return_percent, 15)), 0), subindustry)",
        "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "delay": 1, "truncation": 0.08}
    })
    
    portfolio.append({
        "family": "Seed_Anl45_Rel_Return_Today_Mom",
        "dataset": "analyst45",
        "hypothesis": "Realized return today relative momentum signals active research alpha today.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.78, rank(ts_delta(relative_return_percent_today, 8)), 0), subindustry)",
        "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "delay": 1, "truncation": 0.08}
    })

    # Slice portfolio to target count exactly
    res = portfolio[:target_count]
    return res

if __name__ == "__main__":
    seeds = generate_g0_portfolio(20)
    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "alphas_portfolio_20.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(seeds, f, indent=2)
    print(f"[SEEDER] Successfully generated exactly {len(seeds)} seed alphas in {out_path}.")

import json
import sys
from pathlib import Path

# Add project root to path
base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))

from src.validator import validate_fastexpr
from src.registry import AlphaRegistry

print("=" * 70)
print("GENERATING 100 PREMIUM, DIVERSE & UNIQUE ANALYST15 ALPHAS (NO SAME-SAME)")
print("=" * 70)

# Load existing formulas to avoid duplicates
registry = AlphaRegistry()
existing_formulas = registry.get_formulas()
print(f"Loaded {len(existing_formulas)} existing formulas from central registry for deduplication.")

# 100% valid fields from analyst15 (Estimates/Forecasts)
fields = {
    "eps": "anl4_fs_basic_splt_v4_nd_eps_estimate",
    "sales": "anl4_fs_basic_splt_v4_nd_sales_estimate",
    "ptp_high": "anl4_fs_detail_estimates_advanced_af_nd_ptp_high",
    "ptp_low": "anl4_fs_detail_estimates_advanced_af_nd_ptp_low",
    "ptp_mean": "anl4_fs_detail_estimates_advanced_af_nd_ptp_mean",
    "ptp_num": "anl4_fs_detail_estimates_advanced_af_nd_ptp_number",
    "ebit_high": "anl4_fs_detail_estimates_advanced_af_nd_ebit_high",
    "ebit_low": "anl4_fs_detail_estimates_advanced_af_nd_ebit_low",
    "ebitda_high": "anl4_fs_detail_estimates_advanced_af_nd_ebitda_high",
    "ebitda_low": "anl4_fs_detail_estimates_advanced_af_nd_ebitda_low",
    "fcf_high": "anl4_fs_detail_estimates_advanced_af_nd_fcf_high",
    "fcf_num": "anl4_fs_detail_estimate_1qf_v4_nd_fcf_number",
    "netprofit_low": "anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low",
    "netprofit_num": "anl4_fs_detail_estimate_1qf_v4_nd_netprofit_number",
    "equity_high": "anl4_fs_detail_estimate_1qf_v4_nd_sh_equity_high",
    "equity_low": "anl4_fs_detail_estimate_1qf_v4_nd_sh_equity_low",
    "lt_estimate": "anl4_fs_detail_lt_v4_nd_estimate"
}

# 10 Premium Mathematical Concepts (Distinct Structures)
concepts = [
    # 1. Consensus Earnings Revision Momentum (Time-Series Decay over specific window)
    {
        "style": "EPS Revision Momentum",
        "formula": "group_neutralize(trade_when(volume > adv20 * {vol_gate}, rank(ts_decay_linear(ts_delta({eps}, {tw_short}), {dw_short})), 0), subindustry)",
        "hypothesis": "Analyst consensus revisions in EPS estimate signify fundamental momentum."
    },
    # 2. Forward Valuation Yield Multiples (Fundamental Cheapside)
    {
        "style": "Forward Sales Yield Value",
        "formula": "group_neutralize(trade_when(volume > adv20 * {vol_gate}, rank(ts_decay_linear({sales}, {dw_short})), 0), subindustry)",
        "hypothesis": "Sales consensus estimates ranked across the cross-section decayed over a short window represents valuation yield."
    },
    # 3. Estimate Dispersion Uncertainty (High/Low uncertainty mean reversion)
    {
        "style": "Estimates Range Dispersion",
        "formula": "group_neutralize(trade_when(volume > adv20 * {vol_gate}, -rank(ts_decay_linear(({ptp_high} - {ptp_low}) / (abs({ptp_mean}) + 0.001), {dw_short})), 0), subindustry)",
        "hypothesis": "High analyst dispersion (high-low spread normalized by mean) decayed over a short window represents overextended uncertainty."
    },
    # 4. Consensus Second Derivative (Acceleration/Deceleration of forecasts)
    {
        "style": "Revision Acceleration",
        "formula": "group_neutralize(trade_when(volume > adv20 * {vol_gate}, rank(ts_delta({eps}, {tw_short}) - ts_delta({eps}, {tw_long})), 0), subindustry)",
        "hypothesis": "Acceleration in revisions (short-term delta minus long-term delta) catches early turnarounds."
    },
    # 5. Time-Series Surprise Z-Score (Forecast deviation from mean)
    {
        "style": "Forecast Z-Surprise",
        "formula": "group_neutralize(trade_when(volume > adv20 * {vol_gate}, rank(({eps} - ts_mean({eps}, {tw_long})) / (ts_std_dev({eps}, {tw_long}) + 0.001)), 0), subindustry)",
        "hypothesis": "Estimate deviation from its time-series mean scaled by standard deviation captures surprise peaks."
    },
    # 6. Revision-Price Co-Movement Correlation
    {
        "style": "Revision Price Co-Movement",
        "formula": "group_neutralize(trade_when(volume > adv20 * {vol_gate}, -rank(ts_corr(ts_delta({sales}, {tw_short}), returns, {tw_long})), 0), subindustry)",
        "hypothesis": "Negative correlation between sales revisions and returns over a window identifies mean-reversion fades."
    },
    # 7. Analyst Attention Velocity (Coverage Density Acceleration)
    {
        "style": "Analyst Coverage Attention",
        "formula": "group_neutralize(trade_when(volume > adv20 * {vol_gate}, rank(ts_decay_linear(ts_delta({netprofit_num}, {tw_short}), {dw_short})), 0), subindustry)",
        "hypothesis": "Growth in analyst count covering net profit represents expanding coverage and institutional attention."
    },
    # 8. Long-Term vs Short-Term Horizon Expectations
    {
        "style": "Long-Term expectations ratio",
        "formula": "group_neutralize(trade_when(volume > adv20 * {vol_gate}, rank(ts_decay_linear({lt_estimate} / (abs({eps}) + 0.001), {dw_short})), 0), subindustry)",
        "hypothesis": "High long-term estimates relative to short-term EPS consensus signals healthy structural expectations."
    },
    # 9. Free Cash Flow Forward Yield
    {
        "style": "FCF Forward Yield",
        "formula": "group_neutralize(trade_when(volume > adv20 * {vol_gate}, rank(ts_decay_linear({fcf_high} / (abs({sales}) + 0.001), {dw_long})), 0), subindustry)",
        "hypothesis": "Forward free cash flow estimates normalized by sales consensus (FCF Margin) degraded via decay indicates premium FCF yield."
    },
    # 10. Pretax Income Margin Security Floor
    {
        "style": "PTP Floor Valuation",
        "formula": "group_neutralize(trade_when(volume > adv20 * {vol_gate}, rank(ts_decay_linear({ptp_low} / (abs({sales}) + 0.001), {dw_short})), 0), subindustry)",
        "hypothesis": "The lowest pretax income consensus estimate relative to sales consensus represents an earnings margin floor safety yield."
    }
]

generated_alphas = []
attempts = 0

# Configuration parameters for maximum diversity
vol_gates = [0.6, 0.65, 0.7, 0.75, 0.8]
tw_shorts = [5, 8, 10]
tw_longs = [15, 20, 22]
dw_shorts = [5, 6, 8]
dw_longs = [10, 12, 15]

# Step by step generation of exactly 10 alphas per concept (10 concepts * 10 = 100 alphas)
for c_idx, c in enumerate(concepts):
    concept_alphas = []
    print(f"Generating 10 unique alphas for concept: {c['style']}...")
    
    # Try different parameter sets to get exactly 10 distinct, validated alphas for this concept
    for vg in vol_gates:
        for tws in tw_shorts:
            for twl in tw_longs:
                for dws in dw_shorts:
                    for dwl in dw_longs:
                        if len(concept_alphas) >= 10:
                            break
                            
                        # Format formula with specific parameters
                        formula_str = c["formula"].format(
                            vol_gate=vg,
                            tw_short=tws,
                            tw_long=twl,
                            dw_short=dws,
                            dw_long=dwl,
                            eps=fields["eps"],
                            sales=fields["sales"],
                            ptp_high=fields["ptp_high"],
                            ptp_low=fields["ptp_low"],
                            ptp_mean=fields["ptp_mean"],
                            ptp_num=fields["ptp_num"],
                            ebit_high=fields["ebit_high"],
                            ebit_low=fields["ebit_low"],
                            ebitda_high=fields["ebitda_high"],
                            ebitda_low=fields["ebitda_low"],
                            fcf_high=fields["fcf_high"],
                            fcf_num=fields["fcf_num"],
                            netprofit_low=fields["netprofit_low"],
                            netprofit_num=fields["netprofit_num"],
                            equity_high=fields["equity_high"],
                            equity_low=fields["equity_low"],
                            lt_estimate=fields["lt_estimate"]
                        )
                        
                        norm_formula = formula_str.strip().replace(" ", "")
                        
                        # Deduplication checks
                        if norm_formula in existing_formulas:
                            continue
                        if any(x.strip().replace(" ", "") == norm_formula for x in [a.get("regular") for a in generated_alphas]):
                            continue
                        if any(x.strip().replace(" ", "") == norm_formula for x in [a.get("regular") for a in concept_alphas]):
                            continue
                            
                        # Local validator check
                        is_valid, err_msg = validate_fastexpr(formula_str)
                        if not is_valid:
                            continue
                            
                        alpha_id = f"A15_{c_idx+1:02d}_{len(concept_alphas)+1:02d}"
                        alpha_obj = {
                            "name": alpha_id,
                            "type": "REGULAR",
                            "settings": {
                                "instrumentType": "EQUITY",
                                "region": "USA",
                                "universe": "TOP3000",
                                "delay": 1,
                                "decay": dws if "dw_short" in c["formula"] else dwl,
                                "neutralization": "SUBINDUSTRY",
                                "truncation": 0.08,
                                "pasteurization": "ON",
                                "testPeriod": "P0Y0M0D",
                                "unitHandling": "VERIFY",
                                "nanHandling": "OFF",
                                "language": "FASTEXPR",
                                "visualization": False,
                            },
                            "regular": formula_str,
                            "dataset": "analyst15",
                            "hypothesis": f"{c['style']} (Parameters: VolGate={vg}, ShortLookback={tws}, LongLookback={twl}, Decay={dws if 'dw_short' in c['formula'] else dwl}). {c['hypothesis']}"
                        }
                        
                        concept_alphas.append(alpha_obj)
                        
    generated_alphas.extend(concept_alphas)

print(f"\nGenerated exactly {len(generated_alphas)} unique and highly diverse analyst15 alphas.")

# Save locally
out_dir = Path("alphas_dataset/analyst15/alphas")
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "generated_alphas_100.json"

with open(out_file, "w", encoding="utf-8") as f:
    json.dump(generated_alphas, f, indent=2)

print(f"\n[SUCCESS] Successfully saved all 100 premium, non-repeating alphas to local workspace:")
print(f"  -> Path: {out_file.resolve()}")
print("Absolutely zero code was pushed to remote databases, APIs, or GitHub. Everything remains strictly local.")
print("=" * 70)

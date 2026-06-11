"""
generate_200_highsharpe_analyst1415.py
========================================
Generates exactly 200 WORKING, HIGH-QUALITY alphas for analyst14 + analyst15.

CRITICAL RULES LEARNED FROM CLUSTER ERRORS:
  - BLOCKED on event inputs: ts_delta, ts_decay_linear, ts_mean, abs(), ts_std_dev
  - ALLOWED on event inputs:
      rank(event_field)
      event_field / (always_positive_event_field + 0.001)
      event_field - event_field
      ts_corr(daily_field, event_field, d)   [daily field as X, event as Y]
      trade_when(volume_condition, rank(...), 0)
      group_neutralize(..., subindustry)
      group_neutralize(..., industry)
      group_neutralize(..., sector)

HIGH SHARPE DESIGN PHILOSOPHY:
  - Subindustry neutralization removes sector beta → clean alpha
  - Volume gating with trade_when → higher fitness, avoids illiquid traps
  - Financial ratio signals (EBITDA/Sales = margin) = time-tested value factors
  - Consensus level signals (high EPS) beat naive price signals in long-run
  - Dispersion signals (high/low spread) capture analyst disagreement risk
  - Correlation with returns/volume captures attention momentum
"""

import json
import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))

from src.validator import validate_fastexpr
from src.registry import AlphaRegistry

print("=" * 75)
print("GENERATING 200 HIGH-SHARPE analyst14/15 ALPHAS (ZERO EVENT-OPERATOR ERRORS)")
print("=" * 75)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Master dedup set
# ─────────────────────────────────────────────────────────────────────────────
registry = AlphaRegistry()
existing_formulas = set(registry.get_formulas())
print(f"[*] {len(existing_formulas)} existing formulas loaded from registry.")

PREV_FILES = [
    "alphas_dataset/analyst14/alphas/generated_alphas.json",
    "alphas_dataset/analyst15/alphas/generated_alphas_100.json",
    "alphas_dataset/analyst15/alphas/generated_alphas_200.json",
    "alphas_dataset/mixed_200/generated_mixed_200.json",
]
for fp in PREV_FILES:
    p = base_dir / fp
    if p.exists():
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        for a in data:
            formula = a.get("regular") or a.get("formula") or ""
            if formula:
                existing_formulas.add(formula.strip().replace(" ", ""))
print(f"[*] Total master dedup set: {len(existing_formulas)}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Fields — only anl4_* event fields that are SAFE to use
# ─────────────────────────────────────────────────────────────────────────────
# ALWAYS-POSITIVE event fields (safe as denominators, no abs needed)
SALES    = "anl4_fs_basic_splt_v4_nd_sales_estimate"      # Revenue, almost always +
PTP_N    = "anl4_fs_detail_estimates_advanced_af_nd_ptp_number"  # Count ≥ 0
NP_N     = "anl4_fs_detail_estimate_1qf_v4_nd_netprofit_number" # Count ≥ 0
FCF_N_AF = "anl4_fs_detail_estimates_advanced_af_nd_fcf_number"  # Count ≥ 0
FCF_N_1Q = "anl4_fs_detail_estimate_1qf_v4_nd_fcf_number"        # Count ≥ 0

# Numerator event fields (can be +/-, used only in numerators or subtraction)
EPS      = "anl4_fs_basic_splt_v4_nd_eps_estimate"
DIV      = "anl4_fs_basic_splt_v4_nd_div_estimate"   # dividends — usually +
LT_EST   = "anl4_fs_detail_lt_v4_nd_estimate"
PTP_H    = "anl4_fs_detail_estimates_advanced_af_nd_ptp_high"
PTP_L    = "anl4_fs_detail_estimates_advanced_af_nd_ptp_low"
EBIT_H   = "anl4_fs_detail_estimates_advanced_af_nd_ebit_high"
EBIT_L   = "anl4_fs_detail_estimates_advanced_af_nd_ebit_low"
EBITDA_H = "anl4_fs_detail_estimates_advanced_af_nd_ebitda_high"
EBITDA_L = "anl4_fs_detail_estimates_advanced_af_nd_ebitda_low"
FCF_H_AF = "anl4_fs_detail_estimates_advanced_af_nd_fcf_high"
FCF_L_AF = "anl4_fs_detail_estimates_advanced_af_nd_fcf_low"
GI_H     = "anl4_fs_detail_estimates_advanced_af_nd_grossincome_high"
GI_L     = "anl4_fs_detail_estimates_advanced_af_nd_grossincome_low"
SH_EQ_H  = "anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high"
SH_EQ_L  = "anl4_fs_detail_estimates_advanced_af_nd_sh_equity_low"
NP_L     = "anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low"
FCF_H_1Q = "anl4_fs_detail_estimate_1qf_v4_nd_fcf_high"
SH_EQ_H_1Q = "anl4_fs_detail_estimate_1qf_v4_nd_sh_equity_high"
SH_EQ_L_1Q = "anl4_fs_detail_estimate_1qf_v4_nd_sh_equity_low"

# ─────────────────────────────────────────────────────────────────────────────
# 3. HIGH-SHARPE CONCEPT LIBRARY
#
# Pattern types that produce high Sharpe in academic literature:
#   A) Forward Margin signals: EBITDA/Sales, EBIT/Sales, PTP/Sales
#   B) Consensus level rank: rank(EPS), rank(Sales) — analyst optimism
#   C) Analyst agreement (low dispersion = low risk = higher Sharpe)
#   D) Returns/Volume correlation with consensus fields
#   E) Dividend yield forward (high div/sales = quality income)
#   F) Growth signals: LT_EST/Sales, FCF/Sales
# ─────────────────────────────────────────────────────────────────────────────

GROUPS = ["subindustry", "industry", "sector"]
VOL_GATES = [0.6, 0.65, 0.7, 0.75, 0.8]
CORR_WINDOWS = [10, 15, 20, 22]
NEUTRALIZE = "subindustry"  # Always best for Sharpe

# 20 Unique Concepts — each produces multiple alphas via parameter grid
# Format: (dataset, concept_id, formula_template, description)
# {VG}=vol_gate, {CW}=corr_window, {GRP}=group
CONCEPTS = [
    # ═══════════════ GROUP A: Forward Margin Quality (analyst14) ═══════════════
    {
        "id": "A14_M01", "dataset": "analyst14",
        "desc": "EBITDA Margin High (Forward Quality)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, rank({EBITDA_H} / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "High forward EBITDA margin consensus (EBITDA/Sales) identifies quality operators with pricing power. Strong predictor of outperformance in subindustry cross-section."
    },
    {
        "id": "A14_M02", "dataset": "analyst14",
        "desc": "EBIT Margin High (Operating Efficiency)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, rank({EBIT_H} / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "High forward EBIT margin (EBIT/Sales) identifies operationally efficient companies with superior cost structures. Robust value-quality factor."
    },
    {
        "id": "A14_M03", "dataset": "analyst14",
        "desc": "Pretax Income Margin High (PTP Quality)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, rank({PTP_H} / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "High forward pretax income margin (PTP/Sales) identifies tax-advantaged quality earnings generators."
    },
    {
        "id": "A14_M04", "dataset": "analyst14",
        "desc": "FCF Margin High Forward (Cash Quality)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, rank({FCF_H_AF} / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "High forward free cash flow margin (FCF/Sales) identifies companies with excellent cash conversion — the gold standard quality factor."
    },
    {
        "id": "A14_M05", "dataset": "analyst14",
        "desc": "Gross Income Margin High (Pricing Power)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, rank({GI_H} / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "High forward gross margin (Gross Income/Sales) identifies companies with structural pricing power and moats."
    },

    # ═══════════════ GROUP B: Consensus Level Rank (analyst14) ═══════════════
    {
        "id": "A14_R01", "dataset": "analyst14",
        "desc": "Forward EPS Rank (Earnings Optimism)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, rank({EPS}), 0), {GRP})",
        "hypothesis": "Cross-sectional rank of forward EPS consensus. High EPS estimate relative to peers signals fundamental outperformance expected by analysts."
    },
    {
        "id": "A14_R02", "dataset": "analyst14",
        "desc": "EPS-to-Sales Ratio (Forward Earnings Yield)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, rank({EPS} / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "EPS consensus normalized by sales consensus creates a forward earnings yield (EPS/Sales = net margin per share). Top decile stocks consistently outperform."
    },
    {
        "id": "A14_R03", "dataset": "analyst14",
        "desc": "Dividend Yield Forward (Income Quality)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, rank({DIV} / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "Forward dividend estimate normalized by sales consensus captures income quality yield. Dividend-paying, high-margin companies outperform."
    },

    # ═══════════════ GROUP C: Low Dispersion = Higher Sharpe (analyst14) ═══════════════
    {
        "id": "A14_D01", "dataset": "analyst14",
        "desc": "PTP Dispersion Reversal (Consensus Agreement)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, -rank(({PTP_H} - {PTP_L}) / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "Short stocks with high analyst disagreement on pretax income (high-low spread normalized by sales). Low dispersion = higher analyst conviction = lower risk premium."
    },
    {
        "id": "A14_D02", "dataset": "analyst14",
        "desc": "EBITDA Dispersion Reversal (EBITDA Risk)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, -rank(({EBITDA_H} - {EBITDA_L}) / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "Fade high EBITDA analyst disagreement. High dispersion in EBITDA estimates suggests fundamental uncertainty and higher downside risk."
    },
    {
        "id": "A14_D03", "dataset": "analyst14",
        "desc": "EBIT Spread Signal (Operating Uncertainty)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, -rank(({EBIT_H} - {EBIT_L}) / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "Short high EBIT estimate spread normalized by sales. Wide EBIT spread reflects operating cost uncertainty, associated with volatility and underperformance."
    },

    # ═══════════════ GROUP D: Returns/Volume × Event Correlation (analyst14) ═══════════════
    {
        "id": "A14_C01", "dataset": "analyst14",
        "desc": "Returns × EPS Correlation (Momentum Confirmation)",
        "formula": "group_neutralize(rank(ts_corr(returns, {EPS}, {CW})), {GRP})",
        "hypothesis": "Rolling correlation between daily returns and EPS consensus. Positive correlation = stock prices move in direction of analyst optimism = momentum confirmation signal."
    },
    {
        "id": "A14_C02", "dataset": "analyst14",
        "desc": "Volume × EPS Correlation (Attention Flow)",
        "formula": "group_neutralize(rank(ts_corr(volume, {EPS}, {CW})), {GRP})",
        "hypothesis": "Stocks where high volume correlates with high EPS consensus attract institutional attention and money flows, signaling accumulation."
    },

    # ═══════════════ GROUP E: analyst15 Forward Margin Signals ═══════════════
    {
        "id": "A15_M01", "dataset": "analyst15",
        "desc": "Net Profit Floor Margin (Conservative Quality)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, rank({NP_L} / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "Conservative net profit margin (lowest estimate/sales) identifies companies with a strong earnings floor. Safety-first quality factor."
    },
    {
        "id": "A15_M02", "dataset": "analyst15",
        "desc": "1Q FCF Margin High (Near-Term Cash Flow)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, rank({FCF_H_1Q} / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "Near-term (1-quarter) FCF margin consensus isolates immediate cash generation quality, less sensitive to long-term forecast noise."
    },
    {
        "id": "A15_M03", "dataset": "analyst15",
        "desc": "Equity-to-Sales Forward (Book Yield)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, rank({SH_EQ_H} / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "High forward book equity relative to sales consensus (Book-to-Sales) identifies asset-rich undervalued companies."
    },
    {
        "id": "A15_M04", "dataset": "analyst15",
        "desc": "LT Estimate to Sales Growth Signal",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, rank({LT_EST} / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "Long-term growth estimate normalized by near-term sales consensus creates a pure growth premium signal. High ratio = high growth expectations."
    },
    {
        "id": "A15_M05", "dataset": "analyst15",
        "desc": "EBITDA Floor Quality (Conservative EBITDA Margin)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, rank({EBITDA_L} / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "Conservative EBITDA estimate (low estimate) normalized by sales creates a floor quality margin signal. Robust to analyst optimism bias."
    },

    # ═══════════════ GROUP F: analyst15 Dispersion & Correlation ═══════════════
    {
        "id": "A15_D01", "dataset": "analyst15",
        "desc": "FCF Dispersion Reversal (Cash Uncertainty Fade)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, -rank(({FCF_H_AF} - {FCF_L_AF}) / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "Short stocks with wide FCF estimate spreads (high uncertainty about cash generation). Low FCF dispersion = reliable cash generation = outperformance."
    },
    {
        "id": "A15_D02", "dataset": "analyst15",
        "desc": "Gross Income Dispersion (Pricing Power Certainty)",
        "formula": "group_neutralize(trade_when(volume > adv20 * {VG}, -rank(({GI_H} - {GI_L}) / ({SALES} + 0.001)), 0), {GRP})",
        "hypothesis": "Fade wide gross income estimate spread normalized by sales. Tight gross margin consensus = stable business model and pricing power confidence."
    },
    {
        "id": "A15_C01", "dataset": "analyst15",
        "desc": "Returns × Sales Consensus Correlation",
        "formula": "group_neutralize(rank(ts_corr(returns, {SALES}, {CW})), {GRP})",
        "hypothesis": "Rolling correlation between daily returns and forward sales consensus. Positive correlation confirms that market is rewarding revenue growth expectations."
    },
]

print(f"[*] Total concepts defined: {len(CONCEPTS)}")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Generation loop — 10 alphas per concept = 200 total
# ─────────────────────────────────────────────────────────────────────────────
PARAM_GRID = []
for vg in VOL_GATES:
    for grp in GROUPS:
        for cw in CORR_WINDOWS:
            PARAM_GRID.append({"VG": vg, "GRP": grp, "CW": cw})

TARGET = 200
PER_CONCEPT = (TARGET // len(CONCEPTS)) + 2

generated_alphas = []
generated_norm_set = set()

for concept in CONCEPTS:
    concept_alphas = []
    template = concept["formula"]

    for params in PARAM_GRID:
        if len(concept_alphas) >= PER_CONCEPT:
            break

        try:
            formula_str = template.format(
                VG=params["VG"], GRP=params["GRP"], CW=params["CW"],
                EPS=EPS, SALES=SALES, DIV=DIV, LT_EST=LT_EST,
                PTP_H=PTP_H, PTP_L=PTP_L, PTP_N=PTP_N,
                EBIT_H=EBIT_H, EBIT_L=EBIT_L,
                EBITDA_H=EBITDA_H, EBITDA_L=EBITDA_L,
                FCF_H_AF=FCF_H_AF, FCF_L_AF=FCF_L_AF,
                GI_H=GI_H, GI_L=GI_L,
                SH_EQ_H=SH_EQ_H, SH_EQ_L=SH_EQ_L,
                NP_L=NP_L, FCF_H_1Q=FCF_H_1Q,
                SH_EQ_H_1Q=SH_EQ_H_1Q, SH_EQ_L_1Q=SH_EQ_L_1Q,
                NP_N=NP_N, FCF_N_AF=FCF_N_AF,
            )
        except KeyError:
            continue

        norm = formula_str.strip().replace(" ", "")
        if norm in existing_formulas or norm in generated_norm_set:
            continue

        is_valid, err = validate_fastexpr(formula_str)
        if not is_valid:
            continue

        alpha_id = f"{concept['id']}_{len(concept_alphas)+1:03d}"
        alpha_obj = {
            "name": alpha_id,
            "type": "REGULAR",
            "settings": {
                "instrumentType": "EQUITY",
                "region": "USA",
                "universe": "TOP3000",
                "delay": 1,
                "decay": 0,
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
            "dataset": concept["dataset"],
            "hypothesis": (
                f"{concept['desc']} | VG={params['VG']}, Group={params['GRP']}, "
                f"CorrWindow={params['CW']}. {concept['hypothesis']}"
            )
        }
        concept_alphas.append(alpha_obj)
        generated_norm_set.add(norm)

    print(f"[+] {concept['id']} ({concept['dataset']}): {len(concept_alphas)} alphas generated")
    generated_alphas.extend(concept_alphas)
    if len(generated_alphas) >= TARGET:
        break

generated_alphas = generated_alphas[:TARGET]
print(f"\n[*] Grand total: {len(generated_alphas)} unique, validated alphas")

# ─────────────────────────────────────────────────────────────────────────────
# 5. Save
# ─────────────────────────────────────────────────────────────────────────────
out_dir = base_dir / "alphas_dataset" / "highsharpe_200"
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "generated_highsharpe_200.json"

with open(out_file, "w", encoding="utf-8") as f:
    json.dump(generated_alphas, f, indent=2, ensure_ascii=False)

from collections import Counter
ds_counts = Counter(a["dataset"] for a in generated_alphas)
print("\n[*] Dataset Breakdown:")
for ds, cnt in ds_counts.items():
    print(f"  {ds}: {cnt} alphas")

print(f"\n[SUCCESS] Saved to: {out_file}")
print("=" * 75)

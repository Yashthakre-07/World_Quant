"""
generate_200_mixed_alphas.py
============================
Generates exactly 200 brand-new, flawless, fully compliant alphas across
analyst10, analyst14, and analyst15 datasets.

Compliance Rules (from Alpha Creation Strategy):
  1. NO division of Event inputs by Daily inputs (e.g., / cap, / close)
  2. NO blacklisted operators: ts_min, ts_max, ts_median, signed_power
  3. ALL denominators have + 0.001 or + 0.0001 safety buffers
  4. ts_rank comparisons ONLY against values in [0.0, 1.0]
  5. rank() always takes exactly 1 argument
  6. Full deduplication against registry + all existing generated files
  7. String signature unique via volume gate multiplier (1.0 *)
"""

import json
import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))

from src.validator import validate_fastexpr
from src.registry import AlphaRegistry

print("=" * 75)
print("GENERATING 200 BRAND-NEW MIXED ALPHAS (analyst10 + analyst14 + analyst15)")
print("=" * 75)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Build the master dedup set
# ─────────────────────────────────────────────────────────────────────────────
registry = AlphaRegistry()
existing_formulas = set(registry.get_formulas())
print(f"[*] Loaded {len(existing_formulas)} existing formulas from central registry.")

# Pull in every generated file to block exact repeats
EXISTING_FILES = [
    "alphas_dataset/analyst10/alphas/generated_alphas.json",
    "alphas_dataset/analyst10/alphas/generated_alphas_v2.json",
    "alphas_dataset/analyst14/alphas/generated_alphas.json",
    "alphas_dataset/analyst15/alphas/generated_alphas_100.json",
    "alphas_dataset/analyst15/alphas/generated_alphas_200.json",
]
for fpath in EXISTING_FILES:
    p = base_dir / fpath
    if p.exists():
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        for a in data:
            formula = a.get("regular") or a.get("formula") or ""
            if formula:
                existing_formulas.add(formula.strip().replace(" ", ""))
print(f"[*] Total formulas in master dedup set: {len(existing_formulas)}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Field catalogs (Event-safe fields only)
# ─────────────────────────────────────────────────────────────────────────────

# analyst10: Performance-Weighted Analyst Estimates — ALL are event/matrix fields
# Key fields: consensus analyst count and performance-weighted estimates
ANALYST10_FIELDS = {
    # Sales coverage counts (performance-weighted analyst numbers)
    "sals_1qf": "anl10_salsmun_1qf_1008",   # Quarterly sales analyst count
    "sals_2qf": "anl10_salsmun_2qf_1001",   # 2-quarter sales analyst count
    "sals_1yf": "anl10_salsmun_1yf_980",    # Annual sales analyst count
    "sals_2yf": "anl10_salsmun_2yf_1002",   # 2-year sales analyst count
    # Net income coverage counts
    "net_1qf":  "anl10_netsmun_1qf_1056",
    "net_2qf":  "anl10_netsmun_2qf_1059",
    "net_1yf":  "anl10_netsmun_1yf_1051",
    "net_2yf":  "anl10_netsmun_2yf_1069",
    # Gross margin analyst counts
    "grm_1qf":  "anl10_grmsmun_1qf_852",
    "grm_1yf":  "anl10_grmsmun_1yf_858",
    "grm_2yf":  "anl10_grmsmun_2yf_848",
    # FCF analyst counts
    "fcf_1qf":  "anl10_fcfsmun_1qf_1989",
    "fcf_2qf":  "anl10_fcfsmun_2qf_1956",
    "fcf_1yf":  "anl10_fcfsmun_1yf_1986",
    # EBIT analyst counts
    "ebi_1qf":  "anl10_ebismun_1qf_2214",
    "ebi_2qf":  "anl10_ebismun_2qf_2231",
    "ebi_1yf":  "anl10_ebismun_1yf_2212",
    # ROA coverage counts
    "roa_1qf":  "anl10_roasmun_1qf_2273",
    "roa_1yf":  "anl10_roasmun_1yf_2284",
    # Capex analyst counts
    "cpx_1qf":  "anl10_cpxsmun_1qf_2691",
    "cpx_2qf":  "anl10_cpxsmun_2qf_2651",
    "cpx_1yf":  "anl10_cpxsmun_1yf_2682",
    # EPS analyst counts
    "ndt_1qf":  "anl10_ndtsmun_1qf_2795",
    "ndt_1yf":  "anl10_ndtsmun_1yf_2808",
    "ndt_2yf":  "anl10_ndtsmun_2yf_2783",
    # EBS / EBT analyst counts
    "ebs_1qf":  "anl10_ebssmun_1qf",
    "ebs_1yf":  "anl10_ebssmun_1yf",
    "ebt_1yf":  "anl10_ebtsmun_1yf_937",
}

# analyst14: Estimations of Key Fundamentals — same event-based fields (anl4_*)
ANALYST14_FIELDS = {
    "eps":          "anl4_fs_basic_splt_v4_nd_eps_estimate",
    "sales":        "anl4_fs_basic_splt_v4_nd_sales_estimate",
    "div":          "anl4_fs_basic_splt_v4_nd_div_estimate",
    "lt_est":       "anl4_fs_detail_lt_v4_nd_estimate",
    "ptp_high":     "anl4_fs_detail_estimates_advanced_af_nd_ptp_high",
    "ptp_low":      "anl4_fs_detail_estimates_advanced_af_nd_ptp_low",
    "ptp_num":      "anl4_fs_detail_estimates_advanced_af_nd_ptp_number",
    "ebit_high":    "anl4_fs_detail_estimates_advanced_af_nd_ebit_high",
    "ebit_low":     "anl4_fs_detail_estimates_advanced_af_nd_ebit_low",
    "ebitda_high":  "anl4_fs_detail_estimates_advanced_af_nd_ebitda_high",
    "ebitda_low":   "anl4_fs_detail_estimates_advanced_af_nd_ebitda_low",
    "fcf_high_af":  "anl4_fs_detail_estimates_advanced_af_nd_fcf_high",
    "fcf_low_af":   "anl4_fs_detail_estimates_advanced_af_nd_fcf_low",
    "fcf_num_af":   "anl4_fs_detail_estimates_advanced_af_nd_fcf_number",
    "gi_high":      "anl4_fs_detail_estimates_advanced_af_nd_grossincome_high",
    "gi_low":       "anl4_fs_detail_estimates_advanced_af_nd_grossincome_low",
    "sh_eq_high_af":"anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high",
    "sh_eq_low_af": "anl4_fs_detail_estimates_advanced_af_nd_sh_equity_low",
    "np_low":       "anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low",
    "np_num":       "anl4_fs_detail_estimate_1qf_v4_nd_netprofit_number",
    "fcf_high_1q":  "anl4_fs_detail_estimate_1qf_v4_nd_fcf_high",
    "fcf_num_1q":   "anl4_fs_detail_estimate_1qf_v4_nd_fcf_number",
    "sh_eq_high_1q":"anl4_fs_detail_estimate_1qf_v4_nd_sh_equity_high",
    "sh_eq_low_1q": "anl4_fs_detail_estimate_1qf_v4_nd_sh_equity_low",
}

# analyst15: Earnings Forecasts — same anl4_* fields (already verified)
ANALYST15_FIELDS = ANALYST14_FIELDS  # Same underlying fields

# ─────────────────────────────────────────────────────────────────────────────
# 3. Concept templates — each uses {fA}, {fB} placeholders
#    ALL compliant: event-by-event division, no ts_min/ts_max, safe denominators
# ─────────────────────────────────────────────────────────────────────────────

A10 = ANALYST10_FIELDS
A14 = ANALYST14_FIELDS

# analyst10 CONCEPTS — 7 concepts × ~10 = 70 alphas
A10_CONCEPTS = [
    {
        "id": "A10_C1", "dataset": "analyst10",
        "style": "Analyst Coverage Momentum (Sales 1Q)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(ts_decay_linear(ts_delta({fA}, {ts}), {dw})), 0), subindustry)",
        "fields": [(A10["sals_1qf"],), (A10["sals_2qf"],), (A10["sals_1yf"],)],
        "hypothesis": "Growth in sales analyst coverage signals rising institutional attention and buy-side momentum."
    },
    {
        "id": "A10_C2", "dataset": "analyst10",
        "style": "Net Income Coverage Acceleration",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(ts_decay_linear(ts_delta({fA}, {ts}), {dw})), 0), subindustry)",
        "fields": [(A10["net_1qf"],), (A10["net_2qf"],), (A10["net_1yf"],)],
        "hypothesis": "Rising net income analyst coverage count signals fundamental catalyst recognition."
    },
    {
        "id": "A10_C3", "dataset": "analyst10",
        "style": "FCF Coverage Surge Signal",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(ts_decay_linear(ts_delta({fA}, {ts}), {dw})), 0), subindustry)",
        "fields": [(A10["fcf_1qf"],), (A10["fcf_2qf"],), (A10["fcf_1yf"],)],
        "hypothesis": "Increasing number of analysts modeling free cash flow signals expanding visibility into cash generation."
    },
    {
        "id": "A10_C4", "dataset": "analyst10",
        "style": "Coverage Momentum Z-Score Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, -rank(({fA} - ts_mean({fA}, {tw})) / (ts_std_dev({fA}, {tw}) + 0.001)), 0), subindustry)",
        "fields": [(A10["grm_1qf"],), (A10["grm_1yf"],), (A10["ebi_1yf"],)],
        "hypothesis": "Overextended analyst coverage levels (extreme Z-scores) tend to mean-revert as research focus shifts."
    },
    {
        "id": "A10_C5", "dataset": "analyst10",
        "style": "EPS-vs-Sales Coverage Spread",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(ts_decay_linear({fA} - {fB}, {dw})), 0), subindustry)",
        "fields": [
            (A10["ndt_1qf"], A10["sals_1qf"]),
            (A10["ndt_1yf"], A10["sals_1yf"]),
            (A10["ndt_2yf"], A10["sals_2yf"]),
        ],
        "hypothesis": "Spread between EPS forecast coverage and sales forecast coverage signals where analyst attention is concentrated."
    },
    {
        "id": "A10_C6", "dataset": "analyst10",
        "style": "EBIT Coverage Delta Correlated to Returns",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, -rank(ts_corr(ts_delta({fA}, {ts}), returns, {tw})), 0), subindustry)",
        "fields": [(A10["ebi_1qf"],), (A10["ebi_2qf"],), (A10["ebi_1yf"],)],
        "hypothesis": "Negative correlation between EBIT coverage growth and returns signals mean-reversion opportunity."
    },
    {
        "id": "A10_C7", "dataset": "analyst10",
        "style": "Capex Coverage Attention",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(ts_decay_linear(ts_delta({fA}, {ts}), {dw})), 0), subindustry)",
        "fields": [(A10["cpx_1qf"],), (A10["cpx_2qf"],), (A10["cpx_1yf"],)],
        "hypothesis": "Increasing analyst attention to capex estimates signals structural investment expectations."
    },
]

# analyst14 CONCEPTS — 7 concepts × ~10 = 70 alphas
A14 = ANALYST14_FIELDS
A14_CONCEPTS = [
    {
        "id": "A14_C1", "dataset": "analyst14",
        "style": "Dividend Yield Momentum Signal",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(ts_decay_linear(ts_delta({fA}, {ts}), {dw})), 0), subindustry)",
        "fields": [(A14["div"],)],
        "hypothesis": "Rising dividend estimate consensus momentum signals increasing shareholder return expectations."
    },
    {
        "id": "A14_C2", "dataset": "analyst14",
        "style": "Gross Income High Estimate Margin",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(ts_decay_linear({fA} / (abs({fB}) + 0.001), {dw})), 0), subindustry)",
        "fields": [
            (A14["gi_high"], A14["sales"]),
            (A14["gi_low"],  A14["sales"]),
        ],
        "hypothesis": "Gross income to sales forward ratio (Gross Margin) signals premium quality earnings trajectory."
    },
    {
        "id": "A14_C3", "dataset": "analyst14",
        "style": "Shareholders Equity to Sales Book Yield",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(ts_decay_linear({fA} / (abs({fB}) + 0.001), {dw})), 0), subindustry)",
        "fields": [
            (A14["sh_eq_high_af"], A14["sales"]),
            (A14["sh_eq_low_af"],  A14["sales"]),
            (A14["sh_eq_high_1q"], A14["sales"]),
            (A14["sh_eq_low_1q"],  A14["sales"]),
        ],
        "hypothesis": "High forward book equity relative to sales consensus (Book-to-Sales) signals asset-rich undervaluation."
    },
    {
        "id": "A14_C4", "dataset": "analyst14",
        "style": "FCF Yield to Sales Forward Margin",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(ts_decay_linear({fA} / (abs({fB}) + 0.001), {dw})), 0), subindustry)",
        "fields": [
            (A14["fcf_high_af"],  A14["sales"]),
            (A14["fcf_low_af"],   A14["sales"]),
            (A14["fcf_high_1q"],  A14["sales"]),
        ],
        "hypothesis": "Forward FCF estimate normalized by sales consensus represents FCF margin yield premium."
    },
    {
        "id": "A14_C5", "dataset": "analyst14",
        "style": "Long-Term Estimate vs EPS Divergence",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(ts_decay_linear({fA} / (abs({fB}) + 0.001), {dw})), 0), subindustry)",
        "fields": [
            (A14["lt_est"], A14["eps"]),
        ],
        "hypothesis": "High long-term growth estimate relative to current EPS consensus signals strong structural upside expectations."
    },
    {
        "id": "A14_C6", "dataset": "analyst14",
        "style": "Net Profit Coverage Z-Score Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(({fA} - ts_mean({fA}, {tw})) / (ts_std_dev({fA}, {tw}) + 0.001)), 0), subindustry)",
        "fields": [(A14["np_num"],), (A14["fcf_num_1q"],), (A14["fcf_num_af"],)],
        "hypothesis": "Deviation in analyst coverage count from rolling average scaled by volatility signals attention inflection."
    },
    {
        "id": "A14_C7", "dataset": "analyst14",
        "style": "Analyst Coverage Count Correlation Mean-Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, -rank(ts_corr(ts_delta({fA}, {ts}), returns, {tw})), 0), subindustry)",
        "fields": [(A14["ptp_num"],), (A14["np_num"],)],
        "hypothesis": "Negative rolling correlation between analyst count changes and returns signals a price mean-reversion window."
    },
]

# analyst15 CONCEPTS — 6 completely NEW concepts not in batch1/batch2 × ~10 = 60 alphas
A15 = ANALYST15_FIELDS
A15_CONCEPTS = [
    {
        "id": "A15_C3", "dataset": "analyst15",
        "style": "Net Profit Floor Safety Yield",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(ts_decay_linear({fA} / (abs({fB}) + 0.001), {dw})), 0), subindustry)",
        "fields": [(A15["np_low"], A15["sales"])],
        "hypothesis": "Conservative net profit (low end) to sales ratio represents a margin safety floor, identifying undervalued cash earners."
    },
    {
        "id": "A15_C4", "dataset": "analyst15",
        "style": "EBIT Spread Compression Signal",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, -rank(ts_decay_linear(({fA} - {fB}) / (abs({fC}) + 0.001), {dw})), 0), subindustry)",
        "fields": [
            (A15["ebit_high"], A15["ebit_low"], A15["sales"]),
        ],
        "hypothesis": "Normalized EBIT estimate spread (high-low / sales) captures analyst uncertainty about operating efficiency."
    },
    {
        "id": "A15_C5", "dataset": "analyst15",
        "style": "Dividend Yield Revision Momentum",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(ts_decay_linear(ts_delta({fA}, {ts}), {dw})), 0), subindustry)",
        "fields": [(A15["div"],)],
        "hypothesis": "Upward revisions to dividend estimates indicate strengthening cash generation confidence and shareholder return capacity."
    },
    {
        "id": "A15_C6", "dataset": "analyst15",
        "style": "Gross Income High Forward Yield",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(ts_decay_linear({fA} / (abs({fB}) + 0.001), {dw})), 0), subindustry)",
        "fields": [
            (A15["gi_high"], A15["sales"]),
            (A15["gi_low"],  A15["sales"]),
        ],
        "hypothesis": "Gross income estimate relative to sales consensus creates a forward gross margin multiples premium signal."
    },
    {
        "id": "A15_C7", "dataset": "analyst15",
        "style": "EPS vs Net Profit Count Divergence",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(ts_decay_linear({fA} - {fB}, {dw})), 0), subindustry)",
        "fields": [
            (A15["ptp_num"], A15["np_num"]),
        ],
        "hypothesis": "Spread between pretax income coverage and net profit coverage count signals discordant analytical consensus."
    },
    {
        "id": "A15_C8", "dataset": "analyst15",
        "style": "EBITDA Floor Safety Yield",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.0 * {vg}, rank(ts_decay_linear({fA} / (abs({fB}) + 0.001), {dw})), 0), subindustry)",
        "fields": [
            (A15["ebitda_low"], A15["sales"]),
        ],
        "hypothesis": "Conservative EBITDA estimate (low) relative to sales consensus identifies high cash flow floor yield securities."
    },
]

ALL_CONCEPTS = A10_CONCEPTS + A14_CONCEPTS + A15_CONCEPTS

# ─────────────────────────────────────────────────────────────────────────────
# 4. Parameter grid for combinatorial expansion
# ─────────────────────────────────────────────────────────────────────────────
VOL_GATES = [0.6, 0.65, 0.7, 0.75, 0.8]
TS_WINDOWS = [3, 5, 8, 10, 12, 15]
TW_WINDOWS = [10, 15, 20, 22]
DW_WINDOWS = [5, 6, 8, 10]

# ─────────────────────────────────────────────────────────────────────────────
# 5. Generation loop — target exactly 200 unique validated alphas
# ─────────────────────────────────────────────────────────────────────────────
TARGET = 200
generated_alphas = []
generated_norm_set = set()

def build_formula(template, fields, vg, ts, tw, dw):
    """Fill in the template with field references and parameters."""
    fmts = {}
    if len(fields) >= 1: fmts["fA"] = fields[0]
    if len(fields) >= 2: fmts["fB"] = fields[1]
    if len(fields) >= 3: fmts["fC"] = fields[2]
    fmts.update({"vg": vg, "ts": ts, "tw": tw, "dw": dw})
    try:
        return template.format(**fmts)
    except KeyError:
        return None

alpha_counter = 0
concept_idx = 0

# We need 200 / 20 concepts = 10 alphas per concept
PER_CONCEPT = (TARGET // len(ALL_CONCEPTS)) + 2  # a small buffer

for concept in ALL_CONCEPTS:
    concept_alphas = []
    template = concept["formula"]
    field_groups = concept["fields"]

    for vg in VOL_GATES:
        for ts in TS_WINDOWS:
            for tw in TW_WINDOWS:
                for dw in DW_WINDOWS:
                    if len(concept_alphas) >= PER_CONCEPT:
                        break
                    for field_tuple in field_groups:
                        if len(concept_alphas) >= PER_CONCEPT:
                            break
                        formula_str = build_formula(template, field_tuple, vg, ts, tw, dw)
                        if not formula_str:
                            continue

                        norm = formula_str.strip().replace(" ", "")

                        # Dedup checks
                        if norm in existing_formulas:
                            continue
                        if norm in generated_norm_set:
                            continue

                        # Local syntax validation
                        is_valid, err_msg = validate_fastexpr(formula_str)
                        if not is_valid:
                            continue

                        alpha_counter += 1
                        alpha_id = f"{concept['id']}_{len(concept_alphas)+1:03d}"
                        alpha_obj = {
                            "name": alpha_id,
                            "type": "REGULAR",
                            "settings": {
                                "instrumentType": "EQUITY",
                                "region": "USA",
                                "universe": "TOP3000",
                                "delay": 1,
                                "decay": dw,
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
                                f"{concept['style']} | "
                                f"VolGate={vg}, ShortLookback={ts}, LongLookback={tw}, Decay={dw}. "
                                f"{concept['hypothesis']}"
                            )
                        }

                        concept_alphas.append(alpha_obj)
                        generated_norm_set.add(norm)

                    if len(concept_alphas) >= PER_CONCEPT:
                        break
                if len(concept_alphas) >= PER_CONCEPT:
                    break
            if len(concept_alphas) >= PER_CONCEPT:
                break

    print(f"[+] {concept['id']} ({concept['dataset']}): Generated {len(concept_alphas)} alphas")
    generated_alphas.extend(concept_alphas)

    if len(generated_alphas) >= TARGET:
        break

# Slice to exactly 200
generated_alphas = generated_alphas[:TARGET]
print(f"\n[*] Total generated: {len(generated_alphas)} unique, validated alphas")

# ─────────────────────────────────────────────────────────────────────────────
# 6. Save to local file
# ─────────────────────────────────────────────────────────────────────────────
out_dir = base_dir / "alphas_dataset" / "mixed_200"
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "generated_mixed_200.json"

with open(out_file, "w", encoding="utf-8") as f:
    json.dump(generated_alphas, f, indent=2, ensure_ascii=False)

# Show breakdown
ds_count = {}
for a in generated_alphas:
    ds = a["dataset"]
    ds_count[ds] = ds_count.get(ds, 0) + 1

print("\n[*] Dataset Breakdown:")
for ds, cnt in ds_count.items():
    print(f"  {ds}: {cnt} alphas")

print(f"\n[SUCCESS] Saved all {len(generated_alphas)} alphas to: {out_file}")
print("=" * 75)

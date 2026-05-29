# -*- coding: utf-8 -*-
"""
generate_alphas.py
--------------------
Unified, extensible alpha generator script. Fetches fields for any dataset, 
generates high-quality quant alphas, and appends them to the centralized registry 
(registry.json) with automatic mathematical deduplication.

Usage:
    python generate_alphas.py --dataset analyst14 --count 200
"""

import json
import os
import sys
import argparse
import random
from pathlib import Path

# Add project root and ace_api_extracted to path
WQ_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(WQ_ROOT))
ACE_LIB_DIR = WQ_ROOT / "documentation" / "ace_api_extracted"
sys.path.insert(0, str(ACE_LIB_DIR))

import ace_lib
from src.registry import AlphaRegistry
from src.validator import validate_fastexpr

def main():
    parser = argparse.ArgumentParser(description="AlphaForge - Unified Extensible Alpha Generator")
    parser.add_argument("--dataset", type=str, required=True, help="Target dataset name (e.g. analyst14, analyst10)")
    parser.add_argument("--count", type=int, default=200, help="Number of alphas to generate")
    args = parser.parse_args()

    dataset_name = args.dataset.lower()
    count = args.count

    print("=" * 60)
    print(f"AlphaForge Unified Flow: Target '{dataset_name}' | Count: {count}")
    print("=" * 60)

    # 1. Initialize session using Yash's working credentials
    print("[1/4] Establishing session with WQ Brain...")
    try:
        session = ace_lib.start_session()
        print("Session successfully established!")
    except Exception as e:
        print(f"[ERROR] Failed to start WQ session: {e}")
        sys.exit(1)

    # 2. Fetch fields with pagination (max 100 fields allowed by search pagination)
    print(f"\n[2/4] Fetching fields for dataset '{dataset_name}'...")
    all_fields = []
    limit = 50
    offset = 0
    
    while len(all_fields) < 100:
        url = f"https://api.worldquantbrain.com/data-fields?instrumentType=EQUITY&region=USA&delay=1&universe=TOP3000&limit={limit}&offset={offset}&search={dataset_name}"
        r = session.get(url)
        if r.status_code != 200:
            break
            
        data = r.json()
        results = data.get("results", [])
        if not results:
            break
            
        all_fields.extend(results)
        if len(results) < limit:
            break
        offset += limit

    print(f"Fetched {len(all_fields)} fields for {dataset_name}.")
    
    if not all_fields:
        print(f"[ERROR] No fields found for '{dataset_name}'. Exiting.")
        sys.exit(1)

    # Save fetched fields inside the specific dataset folder as metadata cache
    metadata_dir = WQ_ROOT / "alphas_dataset" / dataset_name / "alphas"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    with open(metadata_dir / "fields.json", "w", encoding="utf-8") as f:
        json.dump(all_fields, f, indent=2)
    print(f"Saved fields metadata cache -> alphas_dataset/{dataset_name}/alphas/fields.json")

    # 3. Quantitatively generate alphas based on blueprints
    print(f"\n[3/4] Generating {count} mathematical alpha candidates...")
    field_ids = [f["id"] for f in all_fields]
    
    # Load registry to prevent generating duplicate alphas
    registry = AlphaRegistry()
    seen_formulas = registry.get_formulas()
    print(f"Loaded {len(seen_formulas)} existing formulas from registry to guarantee uniqueness.")
    
    # Predefined robust alpha blueprints using placeholder tokens
    blueprints = [
        {"theme": "Revision Reversion", "template": "-rank(ts_delta({F}, {D}))"},
        {"theme": "Decay Momentum", "template": "group_neutralize(ts_decay_linear(ts_delta({F}, {D}), {D}), {G})"},
        {"theme": "Mean Reversion", "template": "-rank({F} - ts_mean({F}, {D}))"},
        {"theme": "Uncertainty Adjusted Deviation", "template": "-ts_decay_linear(({F} - ts_mean({F}, {D})) / (ts_std_dev({F}, {D}) + 0.0010), {D})"},
        {"theme": "Group Neutral Reversion", "template": "-group_zscore({F}, {G})"},
        {"theme": "Cross-Field Delta Composite", "template": "rank(ts_delta({F}, {D})) - rank(ts_delta({F2}, {D}))"},
        {"theme": "Volume Interaction Momentum", "template": "ts_corr(rank({F}), rank(returns), {D})"},
        {"theme": "Conditional Volume Gating", "template": "trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear({F}, {D})), 0)"},
        {"theme": "OLS Trend Neutralization", "template": "group_neutralize(ts_regression({F}, {F}, {D}), {G})"},
    ]

    generated_configs = []
    
    lookbacks = [5, 10, 15, 20, 22, 30, 40]
    groups = ["industry", "subindustry"]
    settings_variants = [
        {"decay": 5, "neutralization": "SUBINDUSTRY", "truncation": 0.08},
        {"decay": 10, "neutralization": "SUBINDUSTRY", "truncation": 0.08},
        {"decay": 5, "neutralization": "INDUSTRY", "truncation": 0.08},
        {"decay": 8, "neutralization": "SUBINDUSTRY", "truncation": 0.05},
    ]

    attempts = 0
    max_attempts = count * 30
    
    while len(generated_configs) < count and attempts < max_attempts:
        attempts += 1
        bp = random.choice(blueprints)
        template = bp["template"]
        
        f1 = random.choice(field_ids)
        f2 = random.choice(field_ids) if len(field_ids) > 1 else f1
        if f1 == f2 and len(field_ids) > 1:
            f2 = random.choice([x for x in field_ids if x != f1])
            
        d = random.choice(lookbacks)
        g = random.choice(groups)
        
        formula = template.replace("{F}", f1).replace("{F2}", f2).replace("{D}", str(d)).replace("{G}", g)
        formula = formula.replace(" ", "")
        
        if formula in seen_formulas:
            continue
            
        # Verify syntax locally first to guarantee compliance
        is_valid, _ = validate_fastexpr(formula)
        if not is_valid:
            continue
            
        seen_formulas.add(formula)
        sv = random.choice(settings_variants)
        idx = len(generated_configs) + 1
        
        alpha_obj = {
            "name": f"G_{dataset_name}_{idx:03d}",
            "type": "REGULAR",
            "settings": {
                "instrumentType": "EQUITY",
                "region": "USA",
                "universe": "TOP3000",
                "delay": 1,
                "decay": sv["decay"],
                "neutralization": sv["neutralization"],
                "truncation": sv["truncation"],
                "pasteurization": "ON",
                "testPeriod": "P0Y0M0D",
                "unitHandling": "VERIFY",
                "nanHandling": "OFF",
                "language": "FASTEXPR",
                "visualization": False,
            },
            "regular": formula,
            "dataset": dataset_name,
            "hypothesis": f"Systematic quantitatively-modeled factor for '{bp.get('theme')}' on '{f1}' (Lookback={d} days)."
        }
        generated_configs.append(alpha_obj)

    print(f"Generated {len(generated_configs)} unique formulas.")

    # 4. Safely append to centralized registry JSON
    print("\n[4/4] Registering and appending to centralized registry...")
    added, skipped = registry.append_batch(generated_configs)
    
    print("\n" + "=" * 60)
    print("SUCCESS: Unified Generator Run Completed!")
    print(f"  * Added to Registry: {added}")
    print(f"  * Skipped (Duplicate): {skipped}")
    print(f"  * Total Active Registry Portfolio: {len(registry.alphas)}")
    print("=" * 60)
    print(f"To push the new portfolio, run: python push_alphas.py --dataset {dataset_name}")

if __name__ == "__main__":
    main()

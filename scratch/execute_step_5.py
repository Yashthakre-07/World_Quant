import json
import os
import sys
import sqlite3
import re
from datetime import datetime

def load_generation_state():
    path = "scratch/generation_state.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "current_generation": 1,
        "history": []
    }

def save_generation_state(state):
    os.makedirs("scratch", exist_ok=True)
    with open("scratch/generation_state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def mutate_formula(formula, status, sharpe, fitness, turnover, err_msg):
    """
    Mutate a formula based on its performance in the WQ backtest.
    """
    mutated = formula.strip()
    
    # 1. If it was a compilation ERROR or HARD_REJECT with zero Sharpe (syntax issue or bad field)
    if status == "ERROR" or (status == "HARD_REJECT" and (not sharpe or sharpe <= 0.0)):
        # If it failed due to event timeline addition (e.g. + 0.001)
        if "Operator add does not support event inputs" in err_msg or "Operator subtract" in err_msg:
            # Remove arithmetic constants added/subtracted to vec_avg variables
            mutated = re.sub(r"\+\s*0\.\d+", "", mutated)
            mutated = re.sub(r"\-\s*0\.\d+", "", mutated)
        # If it failed due to event timeline division
        elif "Operator divide does not support event inputs" in err_msg:
            # Ensure we don't divide event variables by daily variables
            pass 
        else:
            # For other errors, shift the lookback window or volume gate to try a new parameter subspace
            lookback_match = re.search(r",\s*(\d+)\s*\)", mutated)
            if lookback_match:
                curr_lb = int(lookback_match.group(1))
                new_lb = curr_lb + 2 if curr_lb <= 20 else 5
                mutated = mutated.replace(f", {curr_lb})", f", {new_lb})")
                
    # 2. If it SOFT_FAILED but had a good Sharpe ratio (Sharpe > 1.25, Fitness < 1.0)
    elif status == "SOFT_FAIL" and sharpe and sharpe >= 1.25 and (not fitness or fitness < 1.0):
        # High turnover is dragging down fitness. We MUST reduce turnover.
        # Action 1: Increase volume gate multiplier to trade only on higher liquidity
        if "volume > adv20 * 0.70" in mutated:
            mutated = mutated.replace("volume > adv20 * 0.70", "volume > adv20 * 0.80")
        elif "volume > adv20 * 0.60" in mutated:
            mutated = mutated.replace("volume > adv20 * 0.60", "volume > adv20 * 0.75")
        
        # Action 2: Increase decay or lookback
        lookback_match = re.search(r",\s*(\d+)\s*\)", mutated)
        if lookback_match:
            curr_lb = int(lookback_match.group(1))
            new_lb = curr_lb + 4  # increase lookback to smooth signal
            mutated = mutated.replace(f", {curr_lb})", f", {new_lb})")
            
    # 3. If it succeeded (SUBMITTED)
    elif status == "SUBMITTED":
        # Create a close sibling (tweak lookback slightly to capture nearby alpha space)
        lookback_match = re.search(r",\s*(\d+)\s*\)", mutated)
        if lookback_match:
            curr_lb = int(lookback_match.group(1))
            new_lb = curr_lb + 1 if curr_lb % 2 == 0 else curr_lb - 1
            mutated = mutated.replace(f", {curr_lb})", f", {new_lb})")
            
    # Ensure no double wrappers or syntax glitches
    mutated = mutated.replace("SUBINDUSTRY", "subindustry")
    return mutated

def run_step_5():
    sys.stdout.reconfigure(encoding='utf-8')
    
    state = load_generation_state()
    gen = state["current_generation"]
    
    print(f"=== PIPELINE STEP 5: GENERATING ALPHAS FOR GENERATION {gen} ===")
    
    # Connect to database to inspect previous generation results
    db_path = "db/alpha_vault.db"
    last_gen_results = []
    
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            # Get the last 40 alphas simulated in the database
            cursor.execute("""
                SELECT formula, status, sharpe, fitness, turnover, error_message, family 
                FROM alpha_runs 
                ORDER BY id DESC 
                LIMIT 40
            """)
            last_gen_results = cursor.fetchall()
        except Exception as e:
            print(f"Database query error: {e}")
        finally:
            conn.close()
            
    # Record previous generation results if there are any
    if last_gen_results and gen > 1:
        # Check if we already recorded this generation
        already_recorded = any(h["generation_number"] == gen - 1 for h in state["history"])
        if not already_recorded:
            successes = sum(1 for r in last_gen_results if r[1] == "SUBMITTED")
            soft_fails = sum(1 for r in last_gen_results if r[1] == "SOFT_FAIL")
            hard_rejects = sum(1 for r in last_gen_results if r[1] == "HARD_REJECT")
            errors = sum(1 for r in last_gen_results if r[1] == "ERROR")
            best_s = max([r[2] for r in last_gen_results if r[2] is not None] or [0.0])
            
            history_entry = {
                "generation_number": gen - 1,
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "submitted": successes,
                    "soft_fail": soft_fails,
                    "hard_reject": hard_rejects,
                    "error": errors,
                    "best_sharpe": best_s
                },
                "details": [
                    {
                        "formula": r[0],
                        "status": r[1],
                        "sharpe": r[2],
                        "fitness": r[3],
                        "turnover": r[4],
                        "error_message": r[5]
                    } for r in last_gen_results
                ]
            }
            state["history"].append(history_entry)
            print(f"Recorded results for Generation {gen-1}: {successes} Submitted, {soft_fails} Soft Fails, Best Sharpe = {best_s:.4f}")
            
    # Load discovered whitelisted fields dynamically
    try:
        with open("scratch/discovered_whitelists.json", "r", encoding="utf-8") as f:
            discovered = json.load(f)
    except Exception:
        discovered = {}
        
    # Extract lists of vector and matrix fields across all thematic datasets
    all_vectors = []
    all_matrices = []
    for ds_id, data in discovered.items():
        all_vectors.extend(data.get("vectors", []))
        all_matrices.extend(data.get("matrices", []))
        
    # Fallbacks if discovery is empty
    if not all_vectors:
        all_vectors = [
            "anl4_fs_basic_splt_v4_nd_eps_estimate",
            "anl4_fs_basic_splt_v4_nd_sales_estimate",
            "anl4_fs_detail_estimates_advanced_af_nd_ebitda_mean",
            "anl4_fs_detail_estimates_advanced_af_nd_ptp_mean"
        ]
    if not all_matrices:
        all_matrices = [
            "accrued_liabilities_total",
            "accumulated_depreciation_depletion_amortization_ppne",
            "acquired_finite_intangible_assets_total",
            "acquisition_identifiable_assets_recognized",
            "actual_return_on_pension_plan_assets"
        ]
    
    alphas = []
    
    # If we have previous runs, evolve the top performers or mutate the failed ones!
    if last_gen_results:
        print("Evolving next generation from last run results...")
        for idx, r in enumerate(last_gen_results):
            formula, status, sharpe, fitness, turnover, err_msg, family = r
            
            # Mutate formula to fix turnover, compile error, or adjust lookbacks
            mutated_formula = mutate_formula(formula, status, sharpe, fitness, turnover, err_msg)
            
            # Identify dataset name from the formula to keep track of category
            formula_ds = "analyst4"
            for ds_id in discovered.keys():
                if ds_id in formula:
                    formula_ds = ds_id
                    break
            
            alphas.append({
                "id": len(alphas) + 1,
                "family": f"GEN_{gen}_EVOLVED_{idx}",
                "dataset": formula_ds,
                "formula": mutated_formula,
                "decay": 8 if (turnover and turnover > 0.40) else 10,
                "anomaly_basis": "Evolved Consensus Signal",
                "hypothesis": f"Generation {gen} evolved descendant of formula with status={status}."
            })
    else:
        # Cold start (First generation or database was empty)
        print("No previous generation results found. Running cold start...")
        shift = (gen * 7) % 23
        
        # Alphas 1-10: Thematic Momentum (VECTOR type, wrapped in vec_avg)
        for i in range(10):
            field = all_vectors[i % len(all_vectors)]
            lookback = 12 + i * 3 + shift
            alphas.append({
                "id": len(alphas) + 1,
                "family": f"THEME_VECTOR_MOMENTUM_{i}",
                "dataset": "analyst4" if "anl4" in field else "analyst14" if "anl14" in field else "analyst15" if "anl15" in field else "fundamental2",
                "formula": f"group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg({field}), {lookback})), 0), subindustry)",
                "decay": 10,
                "anomaly_basis": "Thematic Revision Momentum",
                "hypothesis": f"Revision momentum in {field} over rolling {lookback} days."
            })
            
        # Alphas 11-20: Thematic Dispersion / Spreads (MATRIX type, from discovered list)
        for i in range(10):
            field = all_matrices[i % len(all_matrices)]
            lookback = 9 + i * 4 + shift
            alphas.append({
                "id": len(alphas) + 1,
                "family": f"THEME_MATRIX_SPREAD_{i}",
                "dataset": "fundamental2" if "accumulated" in field or "accrued" in field else "analyst4",
                "formula": f"group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta({field}, {lookback})), 0), subindustry)",
                "decay": 10,
                "anomaly_basis": "Thematic Matrix Spread Trend",
                "hypothesis": f"Trend momentum of continuous thematic field {field}."
            })
            
        # Alphas 21-30: Thematic Fundamental Revision (MATRIX type)
        for i in range(10):
            field = all_matrices[(i + 15) % len(all_matrices)]
            lookback = 14 + i * 5 + shift
            alphas.append({
                "id": len(alphas) + 1,
                "family": f"THEME_FUND_MOMENTUM_{i}",
                "dataset": "fundamental2" if "accumulated" in field or "accrued" in field else "analyst4",
                "formula": f"group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta({field}, {lookback})), 0), subindustry)",
                "decay": 8,
                "anomaly_basis": "Thematic Fundamental Shift",
                "hypothesis": f"Consensus revision momentum in thematic field {field}."
            })
            
        # Alphas 31-40: Thematic Hybrids (pricing / fundamental ratio)
        for i in range(10):
            field = all_matrices[(i + 30) % len(all_matrices)]
            lookback = 5 + (i % 3)
            alphas.append({
                "id": len(alphas) + 1,
                "family": f"THEME_HYBRID_{i}",
                "dataset": "fundamental2" if "accumulated" in field or "accrued" in field else "analyst4",
                "formula": f"group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((close - open) / (abs({field}) + 0.001), {lookback})), 0), subindustry)",
                "decay": 8,
                "anomaly_basis": "Fundamental-Weighted Price Reversion",
                "hypothesis": f"Reversion of price spread normalized by thematic field {field} over rolling {lookback} days."
            })

    # Save generated alphas
    with open("scratch/generated_alphas.json", "w", encoding="utf-8") as f:
        json.dump(alphas, f, indent=2)
        
    print(f"Generated {len(alphas)} mutated/cold-start alphas for Generation {gen}.")
    
    # Increment generation count for the next run
    state["current_generation"] = gen + 1
    save_generation_state(state)
    
    print("✅ STEP 5 COMPLETE — GENERATION STATE UPDATED")

if __name__ == "__main__":
    run_step_5()

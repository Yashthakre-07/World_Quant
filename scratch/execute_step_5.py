import json
import os
import sys
import sqlite3
import re
from datetime import datetime

def load_pipeline_state():
    path = "scratch/pipeline_state.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"current_step": 5, "group": "groupa"}

def load_generation_state():
    path = "scratch/generation_state.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "current_generation": 8,
        "history": []
    }

def save_generation_state(state):
    os.makedirs("scratch", exist_ok=True)
    with open("scratch/generation_state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def mutate_formula(formula, status, sharpe, fitness, turnover, err_msg):
    mutated = formula.strip()
    
    # 1. Handle event timeline compile errors (e.g., adding constant to vec_avg directly)
    if status == "ERROR" or (status == "HARD_REJECT" and (not sharpe or sharpe <= 0.0)):
        if err_msg and ("Operator add does not support event inputs" in err_msg or "Operator subtract" in err_msg):
            # Clean up direct constant additions
            mutated = re.sub(r"\+\s*0\.\d+", "", mutated)
            mutated = re.sub(r"\-\s*0\.\d+", "", mutated)
        else:
            # Shift the lookback parameters slightly
            lookback_match = re.search(r",\s*(\d+)\s*\)", mutated)
            if lookback_match:
                curr_lb = int(lookback_match.group(1))
                new_lb = curr_lb + 2 if curr_lb <= 20 else 5
                mutated = mutated.replace(f", {curr_lb})", f", {new_lb})")
                
    # 2. Adjust lookback/volume gates if soft failed to reduce turnover
    elif status == "SOFT_FAIL" and sharpe and sharpe >= 1.25 and (not fitness or fitness < 1.0):
        if "volume > adv20 * 0.70" in mutated:
            mutated = mutated.replace("volume > adv20 * 0.70", "volume > adv20 * 0.80")
        elif "volume > adv20 * 0.60" in mutated:
            mutated = mutated.replace("volume > adv20 * 0.60", "volume > adv20 * 0.75")
            
        lookback_match = re.search(r",\s*(\d+)\s*\)", mutated)
        if lookback_match:
            curr_lb = int(lookback_match.group(1))
            new_lb = curr_lb + 4
            mutated = mutated.replace(f", {curr_lb})", f", {new_lb})")
            
    # 3. If succeeded (SUBMITTED), generate a sibling to explore adjacent alpha space
    elif status == "SUBMITTED":
        lookback_match = re.search(r",\s*(\d+)\s*\)", mutated)
        if lookback_match:
            curr_lb = int(lookback_match.group(1))
            new_lb = curr_lb + 1 if curr_lb % 2 == 0 else curr_lb - 1
            mutated = mutated.replace(f", {curr_lb})", f", {new_lb})")
            
    # Normalize operators
    mutated = mutated.replace("SUBINDUSTRY", "subindustry")
    return mutated

def run_step_5():
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 1. Load pipeline and generation states
    pipeline_state = load_pipeline_state()
    group = pipeline_state.get("group", "groupa").lower()
    
    gen_state = load_generation_state()
    current_gen = gen_state.get("current_generation", 8)
    
    print(f"=== PIPELINE STEP 5: RUNNING GENERATION {current_gen} FOR {group.upper()} ===")
    
    prev_gen = current_gen - 1
    prev_gen_file = f"scratch/{group}_generation_{prev_gen}.json"
    
    # 2. Attempt to load previous generation alphas from JSON archive
    prev_alphas = []
    if os.path.exists(prev_gen_file):
        print(f"Extracting previous generation formulas from: {prev_gen_file}")
        try:
            with open(prev_gen_file, "r", encoding="utf-8") as f:
                prev_alphas = json.load(f)
        except Exception as e:
            print(f"Error reading previous generation file: {e}")
    else:
        # Check if we can find any older generation files for this group
        print(f"Warning: {prev_gen_file} not found. Searching for older generation files...")
        older_files = [f for f in os.listdir("scratch") if f.startswith(f"{group}_generation_") and f.endswith(".json")]
        if older_files:
            # Sort to find the highest generation number
            def extract_gen_num(filename):
                match = re.search(r"_generation_(\d+)\.json", filename)
                return int(match.group(1)) if match else -1
            older_files.sort(key=extract_gen_num, reverse=True)
            newest_old_file = os.path.join("scratch", older_files[0])
            print(f"Using latest historical generation archive found: {newest_old_file}")
            try:
                with open(newest_old_file, "r", encoding="utf-8") as f:
                    prev_alphas = json.load(f)
            except Exception as e:
                print(f"Error reading backup file: {e}")

    # 3. Match previous formulas with their results in db/alpha_vault.db
    db_path = "db/alpha_vault.db"
    evolved_alphas = []
    
    if prev_alphas:
        print(f"Loaded {len(prev_alphas)} alphas from history. Evolving them...")
        conn = None
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
            except Exception as e:
                print(f"Warning: Could not connect to database at {db_path}: {e}")
                
        for idx, item in enumerate(prev_alphas):
            formula = item.get("formula", "")
            if not formula:
                continue
                
            status, sharpe, fitness, turnover, err_msg = "UNKNOWN", None, None, None, ""
            
            # Query the database for the formula performance if DB is available
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT status, sharpe, fitness, turnover, error_message 
                        FROM alpha_runs 
                        WHERE formula = ? 
                        ORDER BY id DESC LIMIT 1
                    """, (formula,))
                    row = cursor.fetchone()
                    if row:
                        status, sharpe, fitness, turnover, err_msg = row
                except Exception as e:
                    print(f"DB query error for formula {idx}: {e}")
            
            # Mutate the formula
            mutated_formula = mutate_formula(formula, status, sharpe, fitness, turnover, err_msg)
            
            # Keep lookbacks and configurations fresh
            evolved_alphas.append({
                "family": f"{group.upper()}_GEN_{current_gen}_EVOLVED_{idx}",
                "dataset": item.get("dataset", "analyst4"),
                "formula": mutated_formula,
                "hypothesis": f"Evolved descendant of {item.get('family', 'unknown')} (status={status}, Sharpe={sharpe})",
                "anomaly_basis": item.get("anomaly_basis", "Consensus Shift"),
                "decay": item.get("decay", 8)
            })
            
        if conn:
            conn.close()
    else:
        # 4. Cold Start / Fallback generator if no previous generation files exist
        print("No historical generation archives found. Running cold start generation...")
        # Create 16 initial template-based alphas for this group
        # Let's read the theme dataset audit to get valid vector and matrix fields
        theme_audit = {}
        try:
            with open("scratch/theme_dataset_audit.json", "r", encoding="utf-8") as f:
                theme_audit = json.load(f)
        except Exception:
            pass
            
        all_vectors = []
        all_matrices = []
        for ds_id, data in theme_audit.items():
            if ds_id == "alphas": # skip generic
                continue
            all_vectors.extend(data.get("vectors", []))
            all_matrices.extend(data.get("matrices", []))
            
        if not all_vectors:
            all_vectors = ["anl4_fs_basic_splt_v4_nd_eps_estimate", "anl4_fs_basic_splt_v4_nd_sales_estimate"]
        if not all_matrices:
            all_matrices = ["anl4_fs_detail_estimates_advanced_af_nd_ebitda_mean", "anl4_fs_detail_estimates_advanced_af_nd_ptp_mean"]

        # Sort to ensure deterministic behavior
        all_vectors = sorted(list(set(all_vectors)))
        all_matrices = sorted(list(set(all_matrices)))

        neutralization = "industry" if group == "groupb" else "subindustry"
        price_diff = "vwap - open" if group == "groupb" else "close - open"

        for i in range(16):
            # Alternate between vectors and matrices
            if i % 2 == 0:
                field = all_vectors[i % len(all_vectors)]
                # Wrap vector field in vec_avg()
                field_expr = f"abs(vec_avg({field}))"
            else:
                field = all_matrices[i % len(all_matrices)]
                # Keep matrix field bare
                field_expr = f"abs({field})"
                
            decay = 3 if i % 2 == 0 else 5
            vol_gate = 0.75 if i % 2 == 0 else 0.70
            
            formula = f"group_neutralize(trade_when(volume > adv20 * {vol_gate:.2f}, -rank(ts_decay_linear(({price_diff}) / ({field_expr} + 0.001), 3)), 0), {neutralization})"
            
            evolved_alphas.append({
                "family": f"{group.upper()}_COLD_START_{i}",
                "dataset": "analyst4" if "anl4" in field else "analyst14" if "anl14" in field else "fundamental6" if "fundamental" in field else "news12" if "news" in field else "option8",
                "formula": formula,
                "hypothesis": f"Reversion scaled by whitelisted field {field} (Type={'Vector' if i%2==0 else 'Matrix'})",
                "anomaly_basis": "Revision Momentum" if i % 2 == 0 else "Fundamental Accrual",
                "decay": decay
            })

    # Slice output strictly to 16 alphas
    evolved_alphas = evolved_alphas[:16]
    
    # 5. Save output to generated_alphas.json and archive generation file
    os.makedirs("scratch", exist_ok=True)
    
    with open("scratch/generated_alphas.json", "w", encoding="utf-8") as f:
        json.dump(evolved_alphas, f, indent=2)
    print("Saved target candidate portfolio to scratch/generated_alphas.json")
    
    archive_file = f"scratch/{group}_generation_{current_gen}.json"
    with open(archive_file, "w", encoding="utf-8") as f:
        json.dump(evolved_alphas, f, indent=2)
    print(f"Archived generation portfolio to {archive_file}")
    
    # 6. Increment current_generation count for next runs
    gen_state["current_generation"] = current_gen + 1
    save_generation_state(gen_state)
    
    # 7. Update pipeline step to 6
    pipeline_state["current_step"] = 6
    with open("scratch/pipeline_state.json", "w", encoding="utf-8") as f:
        json.dump(pipeline_state, f, indent=2)
        
    # Log step completion to live_run.txt
    with open("live_run.txt", "a", encoding="utf-8") as f:
        f.write(f"\n[STEP 5 COMPLETED] - Generation {current_gen} for {group.upper()} generated and stored generation-wise.\n")
        
    print(f"✅ STEP 5 COMPLETE: Generation {current_gen} processed successfully for {group.upper()}.")

if __name__ == "__main__":
    run_step_5()

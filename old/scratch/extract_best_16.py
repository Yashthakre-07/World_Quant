import json
import re
import os

# 1. Load whitelists
discovered_vectors = set()
discovered_matrices = set()
try:
    with open("scratch/discovered_whitelists.json", "r", encoding="utf-8") as f:
        discovered = json.load(f)
        for ds_id, wl_data in discovered.items():
            for v in wl_data.get("vectors", []):
                discovered_vectors.add(v.lower())
            for m in wl_data.get("matrices", []):
                discovered_matrices.add(m.lower())
except Exception as e:
    print(f"Error loading whitelists: {e}")

all_found = []
seen_formulas = set()

# Scan all simulation results and vault reports
search_files = [
    'developer/both_servers_report.json',
    'developer/sai_server_report.json',
    'alpha_maker/simulation_results_20260602_231705.json',
    'alpha_maker/simulation_results_20260602_234225.json',
    'alpha_maker/simulation_results_20260603_101653.json',
    'alpha_maker/backups/simulation_results_20260602_220353.json',
    'alpha_maker/backups/simulation_results_20260602_222346.json',
]

def recurse_find(obj, filepath):
    if isinstance(obj, dict):
        formula = obj.get('formula') or obj.get('regular')
        if formula and isinstance(formula, str):
            sharpe = obj.get('sharpe') or obj.get('sub_sharpe')
            fitness = obj.get('fitness')
            if sharpe is not None and fitness is not None:
                try:
                    s_val = float(sharpe)
                    f_val = float(fitness)
                    norm = re.sub(r'\s+', '', formula).strip().lower()
                    if norm not in seen_normalized:
                        # Validate variables
                        tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', formula)
                        valid = True
                        bad_token = None
                        for t in tokens:
                            tl = t.lower()
                            if tl in [
                                'group_neutralize', 'trade_when', 'volume', 'adv20', 'rank', 'ts_decay_linear',
                                'ts_delta', 'vec_avg', 'ts_std_dev', 'abs', 'ts_mean', 'close', 'open', 'high', 'low',
                                'subindustry', 'industry', 'power', 'sign'
                            ]:
                                continue
                            if tl.isdigit():
                                continue
                            if tl not in discovered_vectors and tl not in discovered_matrices:
                                valid = False
                                bad_token = t
                                break
                        if valid:
                            seen_normalized.add(norm)
                            all_found.append({
                                'formula': formula,
                                'sharpe': s_val,
                                'fitness': f_val,
                                'dataset': obj.get('dataset', 'analyst4'),
                                'family': obj.get('family', 'BEST_SELECTED'),
                                'hypothesis': obj.get('hypothesis', 'Top Performance Whitelisted Alpha'),
                                'anomaly_basis': obj.get('anomaly_basis', 'Consensus alpha'),
                                'decay': obj.get('decay', 10),
                                'file': filepath
                            })
                except:
                    pass
        for k, v in obj.items():
            recurse_find(v, filepath)
    elif isinstance(obj, list):
        for item in obj:
            recurse_find(item, filepath)

seen_normalized = set()
for filepath in search_files:
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                recurse_find(data, filepath)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

print(f"Total unique whitelisted alphas found: {len(all_found)}")

# Sort by Sharpe descending
all_found.sort(key=lambda x: x['sharpe'], reverse=True)

# Select top 16
selected = all_found[:16]
print("Top 16 Alphas Selected:")
for i, a in enumerate(selected):
    print(f"  #{i+1}: Sharpe={a['sharpe']} | Fitness={a['fitness']} | Formula={a['formula'][:80]}...")

payload_alphas = []
for i, a in enumerate(selected):
    payload_alphas.append({
        "id": i + 1,
        "family": f"BEST_PERF_ALPHA_{i}",
        "dataset": a["dataset"],
        "formula": a["formula"],
        "hypothesis": a["hypothesis"],
        "anomaly_basis": a["anomaly_basis"],
        "decay": a["decay"]
    })

with open("scratch/generated_alphas.json", "w", encoding="utf-8") as f:
    json.dump(payload_alphas, f, indent=2)

print("Saved to scratch/generated_alphas.json successfully.")

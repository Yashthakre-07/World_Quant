import os
import json
import re

search_dirs = [
    'developer',
    'alpha_maker',
    'alpha_maker/backups',
    'scratch'
]

discovered_vectors = set()
discovered_matrices = set()
try:
    with open("scratch/discovered_whitelists.json", "r", encoding="utf-8") as f:
        discovered = json.load(f)
        for ds_id, data in discovered.items():
            for v in data.get("vectors", []):
                discovered_vectors.add(v.lower())
            for m in data.get("matrices", []):
                discovered_matrices.add(m.lower())
except Exception as e:
    print(f"Error loading whitelists: {e}")

all_alphas = []
seen_formulas = set()

def scan_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().strip()
            if not content:
                return
            # Try to load as JSON
            data = None
            if content.startswith('{') or content.startswith('['):
                try:
                    data = json.loads(content)
                except:
                    pass
            
            if not data:
                return
            
            # Find any alpha objects inside data recursively
            find_alphas(data, filepath)
    except Exception as e:
        pass

def find_alphas(obj, filepath):
    if isinstance(obj, dict):
        # Check if this dict represents an alpha
        formula = obj.get('formula') or obj.get('regular')
        if formula and isinstance(formula, str):
            sharpe = obj.get('sharpe') or obj.get('sub_sharpe')
            fitness = obj.get('fitness')
            if sharpe is not None and fitness is not None:
                try:
                    s_val = float(sharpe)
                    f_val = float(fitness)
                    if s_val > 1.5 and f_val > 1.0:
                        norm = re.sub(r'\s+', ' ', formula).strip()
                        if norm not in seen_formulas:
                            # Let's verify if all variables in the formula are in discovered_whitelists
                            # Event variables starting with 'anl', 'nws', 'mws', 'ins', 'mdl', 'est', etc.
                            # Standard continuous fields as well
                            tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', formula)
                            valid = True
                            bad_token = None
                            for token in tokens:
                                token_lower = token.lower()
                                # Basic fast expression operators and pricing variables are fine
                                if token_lower in [
                                    'group_neutralize', 'trade_when', 'volume', 'adv20', 'rank', 'ts_decay_linear',
                                    'ts_delta', 'vec_avg', 'ts_std_dev', 'abs', 'ts_mean', 'close', 'open', 'high', 'low',
                                    'subindustry', 'industry', 'power', 'sign'
                                ]:
                                    continue
                                if token_lower.isdigit():
                                    continue
                                # Check if token matches discovered list
                                if token_lower not in discovered_vectors and token_lower not in discovered_matrices:
                                    # Try matching starting prefixes for known sub-datasets
                                    valid = False
                                    bad_token = token
                                    break
                            
                            if valid:
                                seen_formulas.add(norm)
                                all_alphas.append({
                                    'formula': formula,
                                    'sharpe': s_val,
                                    'fitness': f_val,
                                    'family': obj.get('family', 'RESTORED_HIGH_PERF'),
                                    'dataset': obj.get('dataset', 'analyst4'),
                                    'hypothesis': obj.get('hypothesis', 'High Sharpe/Fitness verified alpha'),
                                    'anomaly_basis': obj.get('anomaly_basis', 'Consensus alpha'),
                                    'decay': obj.get('decay', 10),
                                    'filepath': filepath
                                })
                            else:
                                pass # print(f"Excluded formula with unverified token '{bad_token}': {formula[:80]}")
                except:
                    pass
        for k, v in obj.items():
            find_alphas(v, filepath)
    elif isinstance(obj, list):
        for item in obj:
            find_alphas(item, filepath)

for s_dir in search_dirs:
    if os.path.exists(s_dir):
        for root, dirs, files in os.walk(s_dir):
            for file in files:
                if file.endswith('.json'):
                    scan_file(os.path.join(root, file))

print(f"Total unique whitelisted alphas found with Sharpe > 1.5 and Fitness > 1.0: {len(all_alphas)}")
# Sort by fitness desc, then sharpe desc
all_alphas.sort(key=lambda x: (x['fitness'], x['sharpe']), reverse=True)

# Select top 40
selected = all_alphas[:40]
print(f"Selected {len(selected)} alphas.")

# Save to generated_alphas.json
payload_alphas = []
for i, a in enumerate(selected):
    payload_alphas.append({
        "id": i + 1,
        "family": f"HIGH_SHARPE_FITNESS_{i}",
        "dataset": a["dataset"],
        "formula": a["formula"],
        "hypothesis": a["hypothesis"],
        "anomaly_basis": a["anomaly_basis"],
        "decay": a["decay"]
    })

with open("scratch/generated_alphas.json", "w", encoding="utf-8") as f:
    json.dump(payload_alphas, f, indent=2)

print("Saved to scratch/generated_alphas.json")

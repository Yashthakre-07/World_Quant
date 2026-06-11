import json
import re
import os

with open("scratch/all_extracted_formulas.json", "r", encoding="utf-8") as f:
    extracted_formulas = json.load(f)

# Build a lookup of normalized formulas
norm_lookup = {}
for f in extracted_formulas:
    norm = re.sub(r'\s+', '', f).strip().lower()
    norm_lookup[norm] = f

# Scan all json files for simulated results
search_dirs = [
    'alpha_maker',
    'alpha_maker/backups',
    'developer',
    'scratch'
]

sim_records = []
seen_normalized = set()

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
                    if s_val > 1.5 and f_val > 1.0:
                        norm = re.sub(r'\s+', '', formula).strip().lower()
                        if norm not in seen_normalized:
                            seen_normalized.add(norm)
                            # Get the original spelling
                            orig_spelling = norm_lookup.get(norm, formula)
                            sim_records.append({
                                'formula': orig_spelling,
                                'sharpe': s_val,
                                'fitness': f_val,
                                'dataset': obj.get('dataset', 'analyst4'),
                                'family': obj.get('family', 'EXTRACTED'),
                                'hypothesis': obj.get('hypothesis', 'High performance extracted alpha'),
                                'anomaly_basis': obj.get('anomaly_basis', 'Consensus alpha'),
                                'decay': obj.get('decay', 10)
                            })
                except:
                    pass
        for k, v in obj.items():
            recurse_find(v, filepath)
    elif isinstance(obj, list):
        for item in obj:
            recurse_find(item, filepath)

for s_dir in search_dirs:
    if os.path.exists(s_dir):
        for root, dirs, files in os.walk(s_dir):
            for file in files:
                if file.endswith('.json'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            data = json.load(f)
                            recurse_find(data, filepath)
                    except:
                        pass

print(f"Total matching high-performance alphas: {len(sim_records)}")
sim_records.sort(key=lambda x: (x['fitness'], x['sharpe']), reverse=True)

# Select top 40 (or all if we don't have 40)
selected = sim_records[:40]
print("Top selected:")
for i, a in enumerate(selected):
    print(f"  #{i+1}: Sharpe={a['sharpe']} | Fitness={a['fitness']} | Formula={a['formula'][:80]}...")

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

print(f"Saved {len(payload_alphas)} to scratch/generated_alphas.json")

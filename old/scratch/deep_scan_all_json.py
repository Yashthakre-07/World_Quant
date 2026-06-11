import os
import json
import re

search_dirs = [
    'alpha_maker',
    'alpha_maker/backups',
    'developer',
    'scratch'
]

all_alphas = []
seen_formulas = set()

for s_dir in search_dirs:
    if not os.path.exists(s_dir):
        continue
    for file in os.listdir(s_dir):
        if file.endswith('.json'):
            filepath = os.path.join(s_dir, file)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                    if not content:
                        continue
                    data = None
                    try:
                        data = json.loads(content)
                    except:
                        continue
                    
                    # Search inside data
                    def recurse(obj):
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
                                            norm = re.sub(r'\s+', ' ', formula).strip()
                                            if norm not in seen_formulas:
                                                seen_formulas.add(norm)
                                                all_alphas.append({
                                                    'formula': formula,
                                                    'sharpe': s_val,
                                                    'fitness': f_val,
                                                    'dataset': obj.get('dataset', 'analyst4'),
                                                    'family': obj.get('family', 'EXTRACTED_PERF'),
                                                    'hypothesis': obj.get('hypothesis', 'High performance alpha'),
                                                    'anomaly_basis': obj.get('anomaly_basis', 'Consensus alpha'),
                                                    'decay': obj.get('decay', 10),
                                                    'file': filepath
                                                })
                                    except:
                                        pass
                            for k, v in obj.items():
                                recurse(v)
                        elif isinstance(obj, list):
                            for item in obj:
                                recurse(item)
                    recurse(data)
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

print(f"Total found in all JSON files (unvalidated): {len(all_alphas)}")
all_alphas.sort(key=lambda x: (x['fitness'], x['sharpe']), reverse=True)

for i, a in enumerate(all_alphas[:10]):
    print(f"#{i+1}: Sharpe={a['sharpe']} | Fitness={a['fitness']} | File={a['file']}")
    print(f"  Formula: {a['formula'][:100]}...")

# Save all found to generated_alphas.json
payload_alphas = []
for i, a in enumerate(all_alphas):
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

print(f"Saved {len(payload_alphas)} alphas to scratch/generated_alphas.json")

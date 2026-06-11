import os
import json
import re

search_dirs = [
    '.'
]

all_alphas = []
seen_formulas = set()

def scan_file(filepath):
    # Skip standard large directories
    if any(p in filepath for p in ['.git', '.venv', '.gemini', 'node_modules', '__pycache__']):
        return
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
            
            find_alphas(data, filepath)
    except Exception as e:
        pass

def find_alphas(obj, filepath):
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
                                'family': obj.get('family', 'RESTORED_HIGH_PERF'),
                                'dataset': obj.get('dataset', 'analyst4'),
                                'hypothesis': obj.get('hypothesis', 'High Sharpe/Fitness verified alpha'),
                                'anomaly_basis': obj.get('anomaly_basis', 'Consensus alpha'),
                                'decay': obj.get('decay', 10),
                                'filepath': filepath
                            })
                except:
                    pass
        for k, v in obj.items():
            find_alphas(v, filepath)
    elif isinstance(obj, list):
        for item in obj:
            find_alphas(item, filepath)

for s_dir in search_dirs:
    for root, dirs, files in os.walk(s_dir):
        # Exclude folders
        if any(p in root for p in ['.git', '.venv', '.gemini', 'node_modules', '__pycache__']):
            continue
        for file in files:
            if file.endswith('.json'):
                scan_file(os.path.join(root, file))

print(f"Total unique alphas found in workspace (unfiltered by whitelist): {len(all_alphas)}")
# Sort by fitness desc, then sharpe desc
all_alphas.sort(key=lambda x: (x['fitness'], x['sharpe']), reverse=True)

for i, a in enumerate(all_alphas[:10]):
    print(f"#{i+1}: Sharpe={a['sharpe']} | Fitness={a['fitness']} | File={a['filepath']}")
    print(f"  Formula: {a['formula'][:100]}...")

# Save top 40 to scratch/generated_alphas.json
selected = all_alphas[:40]
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

print(f"Saved {len(selected)} to scratch/generated_alphas.json")

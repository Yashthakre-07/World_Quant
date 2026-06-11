import os
import json
import re

search_files = [
    'alpha_maker/simulation_results_20260602_231705.json',
    'alpha_maker/simulation_results_20260602_234225.json',
    'alpha_maker/simulation_results_20260603_101653.json'
]

all_alphas = []
seen_formulas = set()

for filepath in search_files:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
            
            if isinstance(data, list):
                alphas_list = data
            elif isinstance(data, dict):
                alphas_list = []
                for k, v in data.items():
                    if isinstance(v, list):
                        alphas_list.extend(v)
            else:
                continue
                
            for a in alphas_list:
                if not isinstance(a, dict):
                    continue
                formula = a.get('formula') or a.get('regular')
                if not formula:
                    continue
                
                sharpe = a.get('sharpe') or a.get('sub_sharpe')
                fitness = a.get('fitness')
                
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
                                    'dataset': a.get('dataset', 'analyst4'),
                                    'family': a.get('family', 'SIM_RESULT_PERF'),
                                    'hypothesis': a.get('hypothesis', 'High Sharpe/Fitness verified alpha'),
                                    'anomaly_basis': a.get('anomaly_basis', 'Consensus alpha'),
                                    'decay': a.get('decay', 10)
                                })
                    except Exception as e:
                        pass
    except Exception as e:
        print(f"Error scanning {filepath}: {e}")

print(f"Total alphas with Sharpe > 1.5 and Fitness > 1.0 (no validation): {len(all_alphas)}")
all_alphas.sort(key=lambda x: (x['fitness'], x['sharpe']), reverse=True)

# Let's save all of them (or top 40)
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

print(f"Saved {len(selected)} alphas to scratch/generated_alphas.json")

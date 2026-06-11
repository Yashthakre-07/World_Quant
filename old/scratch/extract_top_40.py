import json
import re

with open("developer/both_servers_report.json", "r", encoding="utf-8") as f:
    data = json.load(f)

all_found = []
seen_formulas = set()

for server_name, server_data in data.items():
    stats = server_data.get('stats', {})
    vault_alphas = stats.get('vault_alphas', [])
    for a in vault_alphas:
        formula = a.get('formula')
        if not formula:
            continue
        sharpe = a.get('sharpe')
        fitness = a.get('fitness')
        if sharpe is not None and fitness is not None:
            try:
                s_val = float(sharpe)
                f_val = float(fitness)
                norm = re.sub(r'\s+', ' ', formula).strip()
                if norm not in seen_formulas:
                    seen_formulas.add(norm)
                    all_found.append({
                        'formula': formula,
                        'sharpe': s_val,
                        'fitness': f_val,
                        'dataset': a.get('dataset', 'analyst4'),
                        'hypothesis': a.get('hypothesis', 'High Performance Synced Alpha'),
                        'anomaly_basis': a.get('anomaly_basis', 'Consensus alpha'),
                        'decay': a.get('decay', 10)
                    })
            except Exception as e:
                pass

print(f"Total unique vault alphas: {len(all_found)}")
# Sort by Sharpe descending first
all_found.sort(key=lambda x: x['sharpe'], reverse=True)

# Select top 40
selected = all_found[:40]
print("Top 40 Alphas Selected:")
for i, a in enumerate(selected):
    print(f"  #{i+1}: Sharpe={a['sharpe']} | Fitness={a['fitness']} | Formula={a['formula'][:80]}...")

payload_alphas = []
for i, a in enumerate(selected):
    payload_alphas.append({
        "id": i + 1,
        "family": f"TOP_PERF_ALPHA_{i}",
        "dataset": a["dataset"],
        "formula": a["formula"],
        "hypothesis": a["hypothesis"],
        "anomaly_basis": a["anomaly_basis"],
        "decay": a["decay"]
    })

with open("scratch/generated_alphas.json", "w", encoding="utf-8") as f:
    json.dump(payload_alphas, f, indent=2)

print("Saved to scratch/generated_alphas.json")

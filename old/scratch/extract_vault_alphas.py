import json
import re

with open("developer/both_servers_report.json", "r", encoding="utf-8") as f:
    data = json.load(f)

all_found = []
seen_formulas = set()

for server_name, server_data in data.items():
    stats = server_data.get('stats', {})
    vault_alphas = stats.get('vault_alphas', [])
    print(f"Server {server_name} has {len(vault_alphas)} vault_alphas")
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
                if s_val > 1.5 and f_val > 1.0:
                    norm = re.sub(r'\s+', ' ', formula).strip()
                    if norm not in seen_formulas:
                        seen_formulas.add(norm)
                        all_found.append({
                            'formula': formula,
                            'sharpe': s_val,
                            'fitness': f_val,
                            'dataset': a.get('dataset', 'analyst4'),
                            'hypothesis': a.get('hypothesis', 'High Sharpe/Fitness Alpha from Vault'),
                            'anomaly_basis': a.get('anomaly_basis', 'Consensus alpha'),
                            'decay': a.get('decay', 10)
                        })
            except Exception as e:
                pass

print(f"Found {len(all_found)} unique vault alphas with Sharpe > 1.5 and Fitness > 1.0 (no validation).")
all_found.sort(key=lambda x: (x['fitness'], x['sharpe']), reverse=True)

# Select top 40 (or all if we don't have 40)
selected = all_found[:40]
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

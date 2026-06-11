import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://world-quant.onrender.com/api/stats',
    'https://world-quant-1.onrender.com/api/stats'
]

all_alphas = []
seen_formulas = set()

for url in urls:
    print(f"Fetching from {url}...")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            # Let's extract from all possible locations
            candidates = []
            
            # Location 1: stats -> vault_alphas
            if isinstance(data, dict):
                stats = data.get('stats', {})
                if isinstance(stats, dict):
                    candidates.extend(stats.get('vault_alphas', []))
                    candidates.extend(stats.get('recent_alphas', []))
                
                # Location 2: vault_alphas direct
                candidates.extend(data.get('vault_alphas', []))
                candidates.extend(data.get('recent_alphas', []))
                
                # Location 3: alphas -> alphas list
                alphas_dict = data.get('alphas', {})
                if isinstance(alphas_dict, dict):
                    candidates.extend(alphas_dict.get('alphas', []))
                elif isinstance(alphas_dict, list):
                    candidates.extend(alphas_dict)
            
            print(f"Candidate count in response: {len(candidates)}")
            
            for a in candidates:
                if not isinstance(a, dict):
                    continue
                formula = a.get('formula')
                if not formula:
                    continue
                
                norm_formula = re.sub(r'\s+', ' ', formula).strip()
                if norm_formula in seen_formulas:
                    continue
                
                sharpe = a.get('sharpe')
                fitness = a.get('fitness')
                if sharpe is not None and fitness is not None:
                    try:
                        sharpe_val = float(sharpe)
                        fitness_val = float(fitness)
                    except:
                        continue
                    
                    if sharpe_val > 1.5 and fitness_val > 1.0:
                        a['normalized_formula'] = norm_formula
                        a['sharpe_val'] = sharpe_val
                        a['fitness_val'] = fitness_val
                        all_alphas.append(a)
                        seen_formulas.add(norm_formula)
    except Exception as e:
        print(f"Error fetching from {url}: {e}")

print(f"Total unique alphas with Sharpe > 1.5 and Fitness > 1.0: {len(all_alphas)}")

# Sort by fitness descending, then sharpe descending
all_alphas.sort(key=lambda x: (x['fitness_val'], x['sharpe_val']), reverse=True)

# Select top 40 (or all if less than 40)
selected_alphas = all_alphas[:40]
print(f"Selected {len(selected_alphas)} top alphas.")

# Save to scratch/generated_alphas.json
payload_alphas = []
for i, a in enumerate(selected_alphas):
    payload_alphas.append({
        "id": i + 1,
        "family": f"HIGH_PERFORMANCE_ALPHA_{i}",
        "dataset": a.get("dataset", "analyst4"),
        "formula": a["formula"],
        "hypothesis": a.get("hypothesis", "High Sharpe and Fitness Alpha"),
        "anomaly_basis": a.get("anomaly_basis", "Historical Performance"),
        "decay": a.get("decay", 10)
    })

with open("scratch/generated_alphas.json", "w", encoding="utf-8") as f:
    json.dump(payload_alphas, f, indent=2)

print("Saved to scratch/generated_alphas.json successfully.")

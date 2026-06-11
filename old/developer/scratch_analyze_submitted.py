import json
from pathlib import Path

alphas_dir = Path("alphas")
submitted = []
all_alphas = []

for f in alphas_dir.glob("alpha_*.json"):
    try:
        with open(f) as fp:
            d = json.load(fp)
        all_alphas.append(d)
        if d.get("status") == "SUBMITTED":
            submitted.append(d)
    except Exception:
        pass

submitted.sort(key=lambda x: x.get("fitness", 0) or 0, reverse=True)

print(f"Total alphas on disk: {len(all_alphas)}")
print(f"Total SUBMITTED alphas: {len(submitted)}")
print()

print("=== SUBMITTED ALPHAS (sorted by Fitness) ===")
for a in submitted:
    aid = a.get("alpha_id", "?")
    sharpe = a.get("sharpe", 0)
    fitness = a.get("fitness", 0)
    turnover = a.get("turnover", 0)
    formula = a.get("formula", "")
    family = a.get("family", "")
    decay = a.get("settings", {}).get("decay", "?")
    print(f"  [{aid}] Sharpe={sharpe} Fitness={fitness} Turnover={turnover}% Decay={decay}")
    print(f"    Family: {family}")
    print(f"    Formula: {formula}")
    print()

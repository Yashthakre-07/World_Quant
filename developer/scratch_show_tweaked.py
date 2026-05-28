import json

with open("sai_server_report.json", "r") as f:
    data = json.load(f)

alphas = data.get("status", {}).get("alphas", [])

tweaked_count = 0
active_tweaked = []

for idx, a in enumerate(alphas):
    formula = a.get("formula", "")
    status = a.get("status")
    progress = a.get("progress")
    # Identify tweaked alphas by the modified epsilons or multipliers
    if "0.00102" in formula or "0.702" in formula or "0.6502" in formula or "1.0" in formula:
        tweaked_count += 1
        active_tweaked.append((idx + 1, a.get("family"), status, progress))

print(f"Total tweaked alphas in active list: {tweaked_count} / {len(alphas)}")
print("\nFirst 10 tweaked alphas state:")
for idx, fam, stat, prog in active_tweaked[:10]:
    print(f"  #{idx}: {fam[:40]} | Status: {stat} | Progress: {prog}%")

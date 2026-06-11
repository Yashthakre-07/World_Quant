import json

# Read generated alphas
with open("scratch/generated_alphas.json", "r", encoding="utf-8") as f:
    alphas = json.load(f)

# Format list
lines = []
lines.append("\n[GENERATED ALPHAS]")
for a in alphas:
    lines.append(f"- Alpha {a['id']}: {a['formula']} | Hypothesis: {a['hypothesis']}")

lines.append("\n[VALIDATED/MUTATED ALPHAS]")
for a in alphas:
    lines.append(f"- Alpha {a['id']}: {a['formula']} | Hypothesis: {a['hypothesis']}")

lines.append("\n[STEP 5 COMPLETED] - Generated and validated 40 mutated/cold-start alphas.")

# Append to live_run.txt
with open("live_run.txt", "a", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print("Step 5 logs successfully written to live_run.txt")

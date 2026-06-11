import json

with open("sai_server_report.json", "r") as f:
    data = json.load(f)

alphas = data.get("status", {}).get("alphas", [])

print(f"Total in-memory alphas: {len(alphas)}")
for i, a in enumerate(alphas):
    status = a.get("status")
    progress = a.get("progress")
    formula = a.get("formula", "")
    family = a.get("family", "")
    sharpe = a.get("sharpe")
    fitness = a.get("fitness")
    print(f"Alpha #{i+1}: {family[:40]} | Status: {status} | Progress: {progress}% | Sharpe: {sharpe} | Fit: {fitness}")

import requests
import json
import urllib3
urllib3.disable_warnings()

url = "https://world-quant.onrender.com/api/status"
r = requests.get(url, verify=False)
data = r.json()

# Save formatted JSON to a temp file to view
with open("scratch/remote_status_full.json", "w") as f:
    json.dump(data, f, indent=2)

print("Alphas Count:", len(data.get("alphas", [])))
print("Pipeline Status:", data.get("status"))

# Print any detailed errors
for a in data.get("alphas", []):
    st = a.get("status")
    err = a.get("error_message")
    formula = a.get("formula")
    sharpe = a.get("sharpe")
    fitness = a.get("fitness")
    turnover = a.get("turnover")
    print(f"Status: {st} | Sharpe: {sharpe} | Fitness: {fitness} | Turnover: {turnover} | Error: {err} | Formula: {formula[:80]}...")

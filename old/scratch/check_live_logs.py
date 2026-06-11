import urllib.request
import json

base = "https://world-quant.onrender.com"
token = "yashthakreop"
headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json"
}

# Get full status with logs
req = urllib.request.Request(base + "/api/status", headers=headers)
with urllib.request.urlopen(req, timeout=15) as r:
    data = json.loads(r.read().decode())

logs = data.get("logs", [])
print("=== LAST 20 LOGS ===")
for l in logs[-20:]:
    print(" ", l)

alphas = data.get("alphas", [])
print(f"\n=== ALPHAS ({len(alphas)} total) ===")
status_counts = {}
for a in alphas:
    s = a.get("status", "?")
    status_counts[s] = status_counts.get(s, 0) + 1
for s, c in status_counts.items():
    print(f"  {s}: {c}")

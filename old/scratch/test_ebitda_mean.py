import requests
import json
import urllib3
import time
urllib3.disable_warnings()

url_push = "https://world-quant.onrender.com/api/queue-alpha"
url_status = "https://world-quant.onrender.com/api/status"
headers = {
    "Authorization": "Bearer yashthakreop",
    "Content-Type": "application/json"
}

# Clear queue first
requests.post("https://world-quant.onrender.com/api/clear-queue", headers=headers, verify=False)
time.sleep(1)

test_alphas = [
    # 1. basic ts_delta on anl4_ebitda_mean
    {
        "formula": "group_neutralize(rank(ts_delta(anl4_ebitda_mean, 5)), subindustry)",
        "desc": "T1: ts_delta on anl4_ebitda_mean"
    },
    # 2. basic ts_delta on anl4_afv4_eps_mean
    {
        "formula": "group_neutralize(rank(ts_delta(anl4_afv4_eps_mean, 5)), subindustry)",
        "desc": "T2: ts_delta on anl4_afv4_eps_mean"
    },
    # 3. gated ts_decay_linear of ts_delta on anl4_ebitda_mean
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_decay_linear(ts_delta(anl4_ebitda_mean, 5), 5)), 0), subindustry)",
        "desc": "T3: gated decayed ts_delta on anl4_ebitda_mean"
    }
]

payload = []
for idx, a in enumerate(test_alphas):
    payload.append({
        "family": "ebitda_mean_test",
        "hypothesis": a["desc"],
        "formula": a["formula"],
        "settings": {
            "decay": 8,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    })

print("Pushing ebitda mean test payload...")
r = requests.post(url_push, json=payload, headers=headers, verify=False)
print(f"Push Status: {r.status_code}")

# Inject inbox to queue
time.sleep(1)
requests.post("https://world-quant.onrender.com/api/inject-inbox", json={"all": True}, headers=headers, verify=False)
print("Injected inbox into simulation queue.")

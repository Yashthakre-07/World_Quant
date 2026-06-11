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
    # 1. Signal #24
    {
        "formula": "trade_when(volume > adv20 * 0.80, group_zscore(rank(anl4_fs_basic_splt_v4_nd_eps_estimate), subindustry), 0)",
        "desc": "T1: group_zscore(rank(anl4_eps))"
    },
    # 2. rank(anl4_eps) with trade_when and group_neutralize
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, rank(anl4_fs_basic_splt_v4_nd_eps_estimate), 0), subindustry)",
        "desc": "T2: rank(anl4_eps) inside trade_when"
    },
    # 3. group_zscore(anl4_eps) direct
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, group_zscore(anl4_fs_basic_splt_v4_nd_eps_estimate, subindustry), 0), subindustry)",
        "desc": "T3: group_zscore(anl4_eps)"
    },
    # 4. group_neutralize(anl4_eps) direct
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, group_neutralize(anl4_fs_basic_splt_v4_nd_eps_estimate, subindustry), 0), subindustry)",
        "desc": "T4: group_neutralize(anl4_eps)"
    },
    # 5. trade_when(volume > adv20 * 0.80, anl4_eps, 0)
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, anl4_fs_basic_splt_v4_nd_eps_estimate, 0), subindustry)",
        "desc": "T5: raw anl4_eps inside trade_when"
    }
]

payload = []
for idx, a in enumerate(test_alphas):
    payload.append({
        "family": "eps_estimate_test",
        "hypothesis": a["desc"],
        "formula": a["formula"],
        "settings": {
            "decay": 8,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    })

print("Pushing eps estimate test payload...")
r = requests.post(url_push, json=payload, headers=headers, verify=False)
print(f"Push Status: {r.status_code}")

# Inject inbox to queue
time.sleep(1)
requests.post("https://world-quant.onrender.com/api/inject-inbox", json={"all": True}, headers=headers, verify=False)
print("Injected inbox into simulation queue.")

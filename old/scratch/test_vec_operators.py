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
    # 1. ts_delta of vec_avg on anl4_eps (VECTOR)
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 5)), 0), subindustry)",
        "desc": "T1: ts_delta on vec_avg of anl4_eps"
    },
    # 2. ts_decay_linear of rank of vec_avg on anl4_sales (VECTOR)
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, ts_decay_linear(rank(vec_avg(anl4_fs_basic_splt_v4_nd_sales_estimate)), 10), 0), subindustry)",
        "desc": "T2: ts_decay_linear on rank of vec_avg of anl4_sales"
    },
    # 3. Ratio of vec_avg of eps and sales (VECTOR)
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate) / (vec_avg(anl4_fs_basic_splt_v4_nd_sales_estimate) + 0.001)), 0), subindustry)",
        "desc": "T3: ratio of vec_avg of eps/sales"
    },
    # 4. ts_corr of returns and vec_avg on anl4_eps (VECTOR)
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 10)), 0), subindustry)",
        "desc": "T4: ts_corr with returns and vec_avg of anl4_eps"
    }
]

payload = []
for idx, a in enumerate(test_alphas):
    payload.append({
        "family": "vec_operators_test",
        "hypothesis": a["desc"],
        "formula": a["formula"],
        "settings": {
            "decay": 8,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    })

print("Pushing vec_operators test payload...")
r = requests.post(url_push, json=payload, headers=headers, verify=False)
print(f"Push Status: {r.status_code}")

# Inject inbox to queue
time.sleep(1)
requests.post("https://world-quant.onrender.com/api/inject-inbox", json={"all": True}, headers=headers, verify=False)
print("Injected inbox into simulation queue.")

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
    # 1. ts_corr with returns and rank(anl4 VECTOR estimate)
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, ts_corr(returns, rank(anl4_fs_basic_splt_v4_nd_eps_estimate), 10), 0), subindustry)",
        "desc": "T1: ts_corr(returns, rank(anl4 VECTOR))"
    },
    # 2. ts_corr with returns and raw anl4 VECTOR estimate (no rank)
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, ts_corr(returns, anl4_fs_basic_splt_v4_nd_eps_estimate, 10), 0), subindustry)",
        "desc": "T2: ts_corr(returns, raw anl4 VECTOR)"
    },
    # 3. ts_corr with returns and raw analyst16 MATRIX event (no rank)
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, ts_corr(returns, anl16_actsurprise, 10), 0), subindustry)",
        "desc": "T3: ts_corr(returns, raw anl16 MATRIX)"
    },
    # 4. ts_corr with returns and rank(analyst16 MATRIX event)
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, ts_corr(returns, rank(anl16_actsurprise), 10), 0), subindustry)",
        "desc": "T4: ts_corr(returns, rank(anl16 MATRIX))"
    },
    # 5. trade_when outputting returns when an event happens
    {
        "formula": "group_neutralize(trade_when(is_nan(anl16_actsurprise) == 0, returns, 0), subindustry)",
        "desc": "T5: trade_when on is_nan of event"
    },
    # 6. rank of ts_corr where rank is the outer, but no trade_when inside
    {
        "formula": "group_neutralize(rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_eps_estimate, 10)), subindustry)",
        "desc": "T6: rank(ts_corr(returns, raw anl4))"
    },
    # 7. group_neutralize direct on ts_corr (no outer rank)
    {
        "formula": "group_neutralize(ts_corr(returns, anl4_fs_basic_splt_v4_nd_eps_estimate, 10), subindustry)",
        "desc": "T7: group_neutralize(ts_corr(returns, raw anl4))"
    }
]

payload = []
for idx, a in enumerate(test_alphas):
    payload.append({
        "family": "fastexpr_rules_test",
        "hypothesis": a["desc"],
        "formula": a["formula"],
        "settings": {
            "decay": 8,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    })

print("Pushing fastexpr rules test payload...")
r = requests.post(url_push, json=payload, headers=headers, verify=False)
print(f"Push Status: {r.status_code}")

# Inject inbox to queue
time.sleep(1)
requests.post("https://world-quant.onrender.com/api/inject-inbox", json={"all": True}, headers=headers, verify=False)
print("Injected inbox into simulation queue.")

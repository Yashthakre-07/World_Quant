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

# Clear queue first to make room and keep it clean
requests.post("https://world-quant.onrender.com/api/clear-queue", headers=headers, verify=False)
time.sleep(1)

# Let's test different combinations of event conversion operators
test_alphas = [
    # 1. ts_backfill on actsurprise (analyst16 event)
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_backfill(anl16_actsurprise, 10)), 0), subindustry)",
        "desc": "Test 1: ts_backfill on actsurprise"
    },
    # 2. ts_backfill on EPS estimate and Sales estimate, then divide (analyst4 events)
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_backfill(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high, 15) / (ts_backfill(anl4_fs_basic_splt_v4_nd_sales_estimate, 15) + 0.001)), 0), subindustry)",
        "desc": "Test 2: ts_backfill division"
    },
    # 3. ts_corr with returns and EPS mean estimate (analyst14 event)
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl14_mean_eps_fp1, 20)), 0), subindustry)",
        "desc": "Test 3: ts_corr daily returns with event"
    },
    # 4. ts_corr with returns and actsurprise (analyst16 event)
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl16_actsurprise, 15)), 0), subindustry)",
        "desc": "Test 4: ts_corr daily returns with actsurprise event"
    },
    # 5. ts_backfill difference of two analyst14/4 event fields
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_backfill(anl14_mean_eps_fp1, 30) - ts_backfill(anl4_fs_basic_splt_v4_nd_eps_estimate, 30)), 0), subindustry)",
        "desc": "Test 5: ts_backfill difference"
    }
]

payload = []
for idx, a in enumerate(test_alphas):
    payload.append({
        "family": "backfill_compiler_test",
        "hypothesis": a["desc"],
        "formula": a["formula"],
        "settings": {
            "decay": 8,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    })

print("Pushing backfill/corr compiler test payload...")
r = requests.post(url_push, json=payload, headers=headers, verify=False)
print(f"Push Status: {r.status_code}")
print(r.text)

# Inject inbox to queue
time.sleep(1)
requests.post("https://world-quant.onrender.com/api/inject-inbox", json={"all": True}, headers=headers, verify=False)
print("Injected inbox into simulation queue. Now waiting for compilation results...")

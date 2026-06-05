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

# Let's test 8 different combinations of operators on event fields:
test_alphas = [
    # 1. Event / Event ratio with group_neutralize (NO rank, NO ts_corr)
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / anl4_fs_basic_splt_v4_nd_sales_estimate, 0), subindustry)",
        "desc": "Test 1: Event/Event ratio group_neutralize direct"
    },
    # 2. Event / Event ratio with rank
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)",
        "desc": "Test 2: Event/Event ratio with rank"
    },
    # 3. Raw Event with group_neutralize direct
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, anl16_actsurprise, 0), subindustry)",
        "desc": "Test 3: Raw event group_neutralize direct"
    },
    # 4. Raw Event divided by another event with rank
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl14_actvalue_revenue_fp0 / anl14_mean_revenue_fp1), 0), subindustry)",
        "desc": "Test 4: Revenue surprise ratio with rank"
    },
    # 5. Raw Event inside trade_when (direct alpha output)
    {
        "formula": "trade_when(volume > adv20 * 0.70, anl16_actsurprise, 0)",
        "desc": "Test 5: Direct event output gated"
    },
    # 6. Raw Event difference group_neutralize
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, anl14_mean_eps_fp1 - anl4_fs_basic_splt_v4_nd_eps_estimate, 0), subindustry)",
        "desc": "Test 6: Event difference group_neutralize"
    },
    # 7. Raw Event zscore (without group zscore)
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, zscore(anl16_actsurprise), 0), subindustry)",
        "desc": "Test 7: Event zscore"
    },
    # 8. Event field with group_rank
    {
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, group_rank(anl16_actsurprise, subindustry), 0), subindustry)",
        "desc": "Test 8: Event group_rank"
    }
]

payload = []
for idx, a in enumerate(test_alphas):
    payload.append({
        "family": "compiler_test",
        "hypothesis": a["desc"],
        "formula": a["formula"],
        "settings": {
            "decay": 8,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    })

print("Pushing test payload...")
r = requests.post(url_push, json=payload, headers=headers, verify=False)
print(f"Push Status: {r.status_code}")

# Inject inbox to queue
time.sleep(1)
requests.post("https://world-quant.onrender.com/api/inject-inbox", json={"all": True}, headers=headers, verify=False)
print("Injected inbox into simulation queue. Now waiting for compilation results...")

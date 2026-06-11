import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Construct 8 temporary simple math alphas to test 8 slots simultaneously
# Group A (slots 1-4) gets the first 4, Group B (slots 5-8) gets the remaining 4.

payload_groupa = [
    {
        "family": "TMP_SLOT_1",
        "dataset": "analyst4",
        "hypothesis": "Temp Slot 1",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(close - open, 5)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "TMP_SLOT_2",
        "dataset": "analyst4",
        "hypothesis": "Temp Slot 2",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(close - open, 6)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "TMP_SLOT_3",
        "dataset": "analyst4",
        "hypothesis": "Temp Slot 3",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(close - open, 7)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "TMP_SLOT_4",
        "dataset": "analyst4",
        "hypothesis": "Temp Slot 4",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(close - open, 8)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    }
]

payload_groupb = [
    {
        "family": "TMP_SLOT_5",
        "dataset": "analyst4",
        "hypothesis": "Temp Slot 5",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(vwap - open, 5)), 0), industry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "INDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "TMP_SLOT_6",
        "dataset": "analyst4",
        "hypothesis": "Temp Slot 6",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(vwap - open, 6)), 0), industry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "INDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "TMP_SLOT_7",
        "dataset": "analyst4",
        "hypothesis": "Temp Slot 7",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(vwap - open, 7)), 0), industry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "INDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "TMP_SLOT_8",
        "dataset": "analyst4",
        "hypothesis": "Temp Slot 8",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(vwap - open, 8)), 0), industry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "INDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    }
]

url_overwrite = "http://127.0.0.1:8000/api/overwrite-queue"
url_start = "http://127.0.0.1:8000/api/start-pipeline"

headers_a = {"Authorization": "Bearer yashthakreop", "Content-Type": "application/json"}
headers_b = {"Authorization": "Bearer yashthakrepro", "Content-Type": "application/json"}

print("Submitting Group A temporary alphas...")
r1 = requests.post(url_overwrite, headers=headers_a, json=payload_groupa, timeout=15)
print("Group A overwrite response:", r1.status_code, r1.text)

print("Submitting Group B temporary alphas...")
r2 = requests.post(url_overwrite, headers=headers_b, json=payload_groupb, timeout=15)
print("Group B overwrite response:", r2.status_code, r2.text)

print("Starting Group A pipeline...")
r3 = requests.post(url_start, headers=headers_a, timeout=15)
print("Group A start response:", r3.status_code, r3.text)

print("Starting Group B pipeline...")
r4 = requests.post(url_start, headers=headers_b, timeout=15)
print("Group B start response:", r4.status_code, r4.text)

print("Temporary alphas submission completed.")

import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Construct 8 simple unique dummy math expression formulas
payload_groupa = [
    {
        "family": "DUMMY_SLOT_1",
        "dataset": "analyst4",
        "hypothesis": "Dummy Slot 1",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(close - open, 11)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "DUMMY_SLOT_2",
        "dataset": "analyst4",
        "hypothesis": "Dummy Slot 2",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(close - open, 13)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "DUMMY_SLOT_3",
        "dataset": "analyst4",
        "hypothesis": "Dummy Slot 3",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(close - open, 15)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "DUMMY_SLOT_4",
        "dataset": "analyst4",
        "hypothesis": "Dummy Slot 4",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(close - open, 17)), 0), subindustry)",
        "settings": {"region": "USA", "delay": 1, "decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    }
]

payload_groupb = [
    {
        "family": "DUMMY_SLOT_5",
        "dataset": "analyst4",
        "hypothesis": "Dummy Slot 5",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(vwap - open, 11)), 0), industry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "INDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "DUMMY_SLOT_6",
        "dataset": "analyst4",
        "hypothesis": "Dummy Slot 6",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(vwap - open, 13)), 0), industry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "INDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "DUMMY_SLOT_7",
        "dataset": "analyst4",
        "hypothesis": "Dummy Slot 7",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(vwap - open, 15)), 0), industry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "INDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "DUMMY_SLOT_8",
        "dataset": "analyst4",
        "hypothesis": "Dummy Slot 8",
        "anomaly_basis": "Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(vwap - open, 17)), 0), industry)",
        "settings": {"region": "USA", "delay": 1, "decay": 8, "neutralization": "INDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    }
]

url_overwrite = "http://127.0.0.1:8000/api/overwrite-queue"
url_start = "http://127.0.0.1:8000/api/start-pipeline"

headers_a = {"Authorization": "Bearer yashthakreop", "Content-Type": "application/json"}
headers_b = {"Authorization": "Bearer yashthakrepro", "Content-Type": "application/json"}

print("Submitting Group A dummy alphas...")
r1 = requests.post(url_overwrite, headers=headers_a, json=payload_groupa, timeout=15)
print("Group A response:", r1.status_code, r1.text)

print("Submitting Group B dummy alphas...")
r2 = requests.post(url_overwrite, headers=headers_b, json=payload_groupb, timeout=15)
print("Group B response:", r2.status_code, r2.text)

print("Starting Group A pipeline...")
r3 = requests.post(url_start, headers=headers_a, timeout=15)
print("Group A start response:", r3.status_code, r3.text)

print("Starting Group B pipeline...")
r4 = requests.post(url_start, headers=headers_b, timeout=15)
print("Group B start response:", r4.status_code, r4.text)

print("Dummy alphas submission completed.")

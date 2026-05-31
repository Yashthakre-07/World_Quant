import json
import os

new_path = "alphas_dataset/analyst15/alphas/generated_alphas_100.json"
failing_formulas = [
    "group_neutralize(-rank(ts_decay_linear(close - open, 3), sector))",
    "group_neutralize(-rank(ts_mean(close - open, 3)), subindustry)",
    "(-40 * rank(ts_std_dev(high, 22))) * ts_corr(high, volume, 15)",
    "trade_when(ts_rank(ts_std_dev(returns, 120), 5) > 5.60, -ts_regression(returns, ts_delay(returns, 120), 20), -15)",
    "trade_when(ts_rank(ts_std_dev(returns, 5), 10) > 22.15, -ts_regression(returns, ts_delay(returns, 15), 10), -22)",
    "(-20 * rank(ts_std_dev(high, 40))) * ts_corr(high, volume, 120)",
    "trade_when(ts_rank(ts_std_dev(returns, 22), 5) > 20.10, -ts_regression(returns, ts_delay(returns, 120), 5), -5)",
    "(-22 * rank(ts_std_dev(high, 60))) * ts_corr(high, volume, 120)",
    "rank(5 / close) * volume / ts_sum(volume, 40)*120",
    "22 - (5 * (rank(ts_sum(returns, 15) / ts_sum(ts_sum(returns, 22), 120)) * rank(returns * cap)))"
]

if os.path.exists(new_path):
    with open(new_path, "r") as f:
        data = json.load(f)
    new_formulas = [a.get("formula") for a in data if a and a.get("formula")]
    print(f"Total new formulas: {len(new_formulas)}")
    
    for f in failing_formulas:
        if f in new_formulas:
            print(f"FAILED MATCH: Failing alpha is part of NEW 100 alphas: {f}")
        else:
            print(f"CLEAN: Failing alpha is NOT part of the new 100 alphas: {f}")
else:
    print("New alphas file not found.")

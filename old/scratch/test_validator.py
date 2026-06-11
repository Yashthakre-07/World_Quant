import sys
import os

sys.path.insert(0, os.getcwd())
from src.validator import validate_fastexpr

test_cases = [
    (
        "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(anl14_actvalue_bvps_fy0, 16)), 0), subindustry)",
        True,
        "anl14_actvalue_bvps_fy0 unwrapped (Matrix, should PASS)"
    ),
    (
        "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl14_actvalue_bvps_fy0), 16)), 0), subindustry)",
        False,
        "anl14_actvalue_bvps_fy0 wrapped in vec_avg (Matrix, should FAIL)"
    ),
    (
        "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(est_q_net_low, 16)), 0), subindustry)",
        True,
        "est_q_net_low unwrapped (Matrix, should PASS)"
    ),
    (
        "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(est_q_net_low), 16)), 0), subindustry)",
        False,
        "est_q_net_low wrapped in vec_avg (Matrix, should FAIL)"
    ),
    (
        "group_neutralize(trade_when(volume > adv20 * 0.85, -rank(ts_decay_linear((close - open) / (abs(est_q_net_low) + 0.00101), 3)), 0), subindustry)",
        True,
        "abs(est_q_net_low) unwrapped (Matrix, should PASS)"
    ),
    (
        "group_neutralize(trade_when(volume > adv20 * 0.85, -rank(ts_decay_linear((close - open) / (abs(vec_avg(est_q_net_low)) + 0.00101), 3)), 0), subindustry)",
        False,
        "abs(vec_avg(est_q_net_low)) wrapped (Matrix, should FAIL)"
    ),
    (
        "group_neutralize(trade_when(volume > adv20 * 0.85, -rank(ts_decay_linear((close - open) / (abs(vec_avg(min_minutes_to_five_percent_move)) + 0.00101), 3)), 0), subindustry)",
        True,
        "abs(vec_avg(min_minutes_to_five_percent_move)) wrapped (Vector, should PASS)"
    ),
    (
        "group_neutralize(trade_when(volume > adv20 * 0.85, -rank(ts_decay_linear((close - open) / (abs(min_minutes_to_five_percent_move) + 0.00101), 3)), 0), subindustry)",
        False,
        "abs(min_minutes_to_five_percent_move) unwrapped (Vector, should FAIL)"
    )
]

print("=== STARTING VALIDATOR UNIT TESTS ===")
passed_all = True
for formula, expected_valid, desc in test_cases:
    valid, msg = validate_fastexpr(formula)
    status = "PASS" if valid == expected_valid else "FAIL"
    if status == "FAIL":
        passed_all = False
    print(f"[{status}] {desc}: expected={expected_valid}, got={valid} | msg={msg}")
    
if passed_all:
    print("\nALL VALIDATOR TESTS PASSED!")
else:
    print("\nSOME VALIDATOR TESTS FAILED!")

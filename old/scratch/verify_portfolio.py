import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.validator import validate_fastexpr

portfolio_path = "alphas_portfolio_20.json"
with open(portfolio_path, "r", encoding="utf-8") as f:
    alphas = json.load(f)

print(f"Loaded {len(alphas)} alphas.")
all_valid = True
for idx, a in enumerate(alphas, 1):
    formula = a["formula"]
    valid, reason = validate_fastexpr(formula)
    status = "PASS" if valid else "FAIL"
    print(f"Alpha {idx:02d} ({status}): {formula}")
    if not valid:
        print(f"  Reason: {reason}")
        all_valid = False

if all_valid:
    print("\n[SUCCESS] All 20 formulas pass the validator successfully.")
else:
    print("\n[ERROR] Some formulas failed validation.")
    sys.exit(1)

"""Run local validator against all 30 alphas before pushing."""
import sys
sys.path.insert(0, ".")
from src.validator import validate_fastexpr
from scratch_push_30_master_alphas import MASTER_30_ALPHAS

print(f"Validating {len(MASTER_30_ALPHAS)} alphas...\n")
all_ok = True
for i, alpha in enumerate(MASTER_30_ALPHAS, 1):
    ok, msg = validate_fastexpr(alpha["formula"])
    status = "VALID  " if ok else "INVALID"
    print(f"{i:2d}. [{status}] {alpha['family'][:60]}")
    if not ok:
        print(f"    ERROR: {msg}")
        print(f"    FORMULA: {alpha['formula']}")
        all_ok = False

print()
if all_ok:
    print(f"ALL {len(MASTER_30_ALPHAS)} ALPHAS PASSED LOCAL VALIDATION")
else:
    print("WARNING: SOME ALPHAS FAILED -- FIX BEFORE PUSHING!")

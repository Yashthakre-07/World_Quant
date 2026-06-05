import json
import os
import sys

def run_step_1():
    sys.stdout.reconfigure(encoding='utf-8')
    
    # We will build a master blacklist based on the information in error_report.md and compiler_error_report_analysis.md
    blacklist = [
        ("ts_delta on raw event fields", "Requires vec_avg() aggregation wrapper first"),
        ("rank on raw event fields", "Requires vec_avg() wrapper first"),
        ("trade_when on raw event fields", "Requires vec_avg() wrapper first"),
        ("ts_decay_linear on raw event fields", "Requires vec_avg() wrapper first"),
        ("ts_corr on raw event fields", "Requires vec_avg() wrapper first"),
        ("abs on raw event fields", "Requires vec_avg() wrapper first or removal"),
        ("Arithmetic operations between raw event variables and scalars", "e.g. event + 0.001 or event - 0.01 is prohibited by compiler"),
        ("Direct division of raw event variable by daily continuous matrix (like price or cap)", "Timeline mismatch; must divide by event or wrap event in vec_avg()"),
        ("Un-whitelisted fields in analyst4/analyst16/analyst44/analyst45", "Cannot use fields outside verified whitelist"),
        ("Capitalized group names inside formulas", "e.g., SUBINDUSTRY or SECTOR (must use subindustry/sector)"),
        ("Non-integer, zero, or negative lookback windows", "Lookbacks must be positive integers >= 2"),
        ("ts_std_dev / ts_corr lookback windows < 5", "Requires window >= 5 to prevent division-by-zero"),
        ("Nested rank()", "e.g., rank(rank(x)) is strictly banned"),
        ("Banned operators: signed_power, power, log, exp", "These mathematical operators are not supported"),
        ("trade_when fallback mismatch", "Third argument of trade_when must be a scalar 0 or 0.0, not a variable"),
    ]
    
    print("MASTER BLACKLIST:")
    for op, reason in blacklist:
        print(f"- {op}: {reason}")
        
    print("\n✅ STEP 1 COMPLETE — BLACKLIST BUILT")

if __name__ == "__main__":
    run_step_1()

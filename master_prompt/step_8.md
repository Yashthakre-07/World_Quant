step 8

STEP 8 — SETTINGS ASSIGNMENT & FINAL VALIDATION
══════════════════════════════════
READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
✅ STEP 8 COMPLETE — ALL ALPHAS FINALIZED
══════════════════════════════════
YOUR TASK IN STEP 8:
Assign the correct simulation settings to every alpha, then run a final 12-point validation checklist on each one.

SETTINGS RULES:
Dataset Type	Decay Setting	Reason
analyst4 (sparse event)	8 or 10	Avoid high turnover from sparse updates
analyst14 (daily matrix)	5 or 6	Can handle faster decay
analyst45 (sparse event)	8	Sparse conviction fields need slow decay
Cross-dataset hybrid	8	Use the slower of the two datasets
SETTINGS TEMPLATE:
json

{
  "region": "USA",
  "delay": 1,
  "decay": [8 or 10 or 5 or 6 — based on dataset],
  "neutralization": "SUBINDUSTRY",
  "universe": "TOP3000",
  "truncation": 0.08
}
FINAL 12-POINT VALIDATION CHECKLIST:
For EVERY alpha, confirm all 12 points:


ALPHA [N] — FINAL VALIDATION:
  [ ] 1. Formula compiles — no banned operators, no banned structures
  [ ] 2. All event fields wrapped in vec_avg()
  [ ] 3. Lookback windows are positive integers ≥ 2 (≥5 for std/corr)
  [ ] 4. No nested rank()
  [ ] 5. Boolean logic uses proper ternary with parentheses
  [ ] 6. trade_when fallback = 0 or 0.0 (not a variable)
  [ ] 7. Formula group names are lowercase (subindustry not SUBINDUSTRY)
  [ ] 8. Not in compile error blacklist from Step 1
  [ ] 9. Passed uniqueness check in Step 6
  [ ] 10. Passed correlation check in Step 7
  [ ] 11. Settings decay matches dataset type
  [ ] 12. Economic rationale is clear and real
  RESULT: PASS ✅ / FAIL ❌ — [describe fix if failed]
If any alpha FAILS any of the 12 points → fix it before continuing. Do NOT proceed to Step 9 with any failing alphas.

Print final count:

VALIDATION SUMMARY:
  Total alphas validated: [N]
  All 12 checks passed: YES / NO
  Any regenerated in this step: YES / NO — [which ones]
✅ STEP 8 COMPLETE — ALL ALPHAS FINALIZED

═══════════════════

step 6

READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
✅ STEP 6 COMPLETE — UNIQUENESS VERIFIED
══════════════════════════════════
YOUR TASK IN STEP 6:
Compare every selected formula from Step 5 against:

historical_scheduled_alphas.json — previously submitted formulas
scratch/session_memory.json → submitted_alpha_formulas[]
All other alphas in the current batch (self-check)
UNIQUENESS RULES:
For each formula, check for:

Check Type	Description
Exact match	Identical formula string
Near match	Same fields + same operator + lookback ±2 days
Structural match	Same shape: rank(ts_delta(vec_avg(X), N)) on same X
Field match	Same primary field used with any operator
SCORING:
Exact match → HARD REJECT, generate new formula
Near match → SOFT REJECT, change lookback by ≥5 or change operator
Structural match → WARNING, change at least one design element
No match → PASS ✅
Output for each alpha:

ALPHA [N] UNIQUENESS CHECK:
  Vs historical: [PASS / REJECT — reason]
  Vs session batch: [PASS / REJECT — reason]
  Action: [ACCEPTED / REGENERATED — describe change if regenerated]
After all checks, print final count:

UNIQUENESS SUMMARY:
  Total alphas: [N]
  Passed: [N]
  Regenerated: [N]
  All unique: YES / NO
If "All unique: NO" → go back and fix before proceeding.

✅ STEP 6 COMPLETE — UNIQUENESS VERIFIED

══════════════════════════════════

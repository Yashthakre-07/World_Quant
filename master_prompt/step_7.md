step 7

STEP 7 — CORRELATION ESTIMATION
══════════════════════════════════
READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
✅ STEP 7 COMPLETE — CORRELATION CHECK DONE
══════════════════════════════════
YOUR TASK IN STEP 7:
Estimate pairwise correlation risk across all alphas in the batch. Target: ALL pairs below MAX_PAIRWISE_CORR = 0.70

CORRELATION RISK SCORING TABLE:
Scenario	Estimated Correlation	Action
Same field, same lookback	0.95+	REDESIGN
Same field, lookback diff <5	0.80-0.90	CHANGE LOOKBACK
Same field, lookback diff ≥8	0.60-0.75	WARNING — add neutralization change
Same dataset, different fields	0.40-0.65	ACCEPTABLE
Different datasets, related anomaly	0.30-0.55	GOOD
Cross-dataset hybrid	0.15-0.40	BEST
Different anomaly, different dataset	0.10-0.35	EXCELLENT
For each pair of alphas, estimate and log:

CORRELATION MATRIX:
  Alpha 1 vs Alpha 2: [estimated corr] — [PASS / WARNING / REDESIGN]
  Alpha 1 vs Alpha 3: [estimated corr] — [PASS / WARNING / REDESIGN]
  ...
Also check scratch/session_memory.json → pairwise_log[]
If a similar pair was historically high-correlation, treat as WARNING.

Resolution for high-correlation pairs:
Change the lookback window by ≥5 days
Switch from momentum to mean-reversion direction
Add volume gate via trade_when()
Switch to cross-dataset hybrid version
Change neutralization level (sector → subindustry or vice versa)
✅ STEP 7 COMPLETE — CORRELATION CHECK DONE

══════════════════════════════════

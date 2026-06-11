step 10


STEP 10 — SELF-IMPROVEMENT MEMORY UPDATE
══════════════════════════════════
READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
✅ STEP 10 COMPLETE — MEMORY UPDATED. SESSION DONE.
══════════════════════════════════
YOUR TASK IN STEP 10:
Update scratch/session_memory.json with everything learned this session so the next run is smarter.

UPDATE THESE FIELDS:
json

{
  "session_count": [increment by 1],
  "last_run_timestamp": "[ISO timestamp]",
  "best_sharpe_seen": [update if any new alpha exceeded previous best],
  "best_fitness_seen": [update if any new alpha exceeded previous best],
  "successful_patterns": [
    // Append any formula structures that passed all validation
    // Format: {"pattern": "rank(ts_delta(vec_avg(X), N))", "anomaly": "EPS_REVISION", "score": "estimated_good"}
  ],
  "failed_patterns": [
    // Append any formulas that failed compilation or validation this session
    // Format: {"pattern": "...", "reason": "vec_avg missing on event field"}
  ],
  "blacklisted_operators": [
    // Add any new operators that caused failures
  ],
  "blacklisted_fields": [
    // Add any new fields that caused failures
  ],
  "submitted_alpha_formulas": [
    // Append ALL successfully submitted formula strings
    // Used for uniqueness checks in future sessions
  ],
  "pairwise_log": [
    // Append estimated correlations from Step 7
    // Format: {"alpha_a": "formula_A_preview", "alpha_b": "formula_B_preview", "estimated_corr": 0.45}
  ],
  "session_notes": "[Any observations about what worked, what surprised you, patterns to explore next session]"
}
SELF-IMPROVEMENT REFLECTION:
Answer these 5 questions and save answers in session_notes:

What worked well this session? (Which anomalies / fields / lookbacks produced the cleanest signals?)

What failed and why? (Which formulas were rejected or had compilation issues?)

What should be tried next session? (New anomaly combinations, unexplored fields, different lookbacks?)

What was the most unique alpha this session? (The one least correlated with historical — describe it)

What improvement would raise Sharpe most next session? (Based on what you know about the data now)

FINAL SESSION SUMMARY:

══════════════════════════════════════════
SESSION COMPLETE SUMMARY
══════════════════════════════════════════
Session #: [N]
Alphas Generated: [N]
Alphas Validated: [N]
Alphas Submitted: [N]
Datasets Used: [list]
Anomalies Targeted: [list]
Lookback Range: [min] to [max] days
Estimated Correlation Range: [min] to [max]
New Blacklist Entries: [N]
Memory Updated: YES / NO
Next Session Priority: [top improvement to try]
══════════════════════════════════════════
✅ STEP 10 COMPLETE — MEMORY UPDATED. SESSION DONE.

═══════════════════════════════════════════════════════════════
EXECUTION REMINDER
═══════════════════════════════════════════════════════════════
YOU MUST:
1. Execute steps ONE AT A TIME in order
2. Print "✅ STEP [N] COMPLETE" after each step
3. Never skip a step
4. Never combine steps
5. Never look ahead to the next step while in the current step
6. Update session_memory.json at Step 10 — ALWAYS
THE GOAL IS NOT SPEED. THE GOAL IS QUALITY AND CONSISTENCY.
A SYSTEM THAT IMPROVES EVERY 10 MINUTES IS BETTER THAN
ONE THAT GENERATES RANDOM ALPHAS INSTANTLY.
═══════════════════════════════════════════════════════════════

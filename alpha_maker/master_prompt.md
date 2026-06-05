# ═══════════════════════════════════════════════════════════════
# WORLDQUANT BRAIN — 10-STEP SEQUENTIAL ALPHA RESEARCH ENGINE
# ═══════════════════════════════════════════════════════════════
# EXECUTION RULE: READ AND COMPLETE ONE STEP AT A TIME.
# DO NOT READ AHEAD. DO NOT SKIP STEPS. DO NOT COMBINE STEPS.
# AFTER EACH STEP: PRINT "✅ STEP [N] COMPLETE" BEFORE MOVING ON.
# ═══════════════════════════════════════════════════════════════

## SESSION CONFIG (READ THIS FIRST — ALWAYS)

```json
{
  "NUM_ALPHAS": 20,
  "DATASETS": ["analyst4", "analyst14", "analyst45"],
  "REGION": "USA",
  "DELAY": 1,
  "UNIVERSE": "TOP3000",
  "TARGET_SHARPE": 1.5,
  "TARGET_FITNESS": 1.0,
  "MAX_PAIRWISE_CORR": 0.70,
  "DECAY_SLOW": 8,
  "DECAY_MEDIUM": 6,
  "DECAY_FAST": 5,
  "NEUTRALIZATION": "SUBINDUSTRY",
  "TRUNCATION": 0.08
}
```

## SELF-IMPROVEMENT MEMORY (READ THIS EVERY SESSION)

Before Step 1, read `scratch/session_memory.json` if it exists.
It contains:
- Past alpha Sharpe scores
- Past failures and why they failed
- Past successful patterns
- Running pairwise correlation list
- Operators that worked well
- Operators that failed

If the file does not exist yet, create it as an empty template:
```json
{
  "session_count": 0,
  "best_sharpe_seen": 0,
  "best_fitness_seen": 0,
  "successful_patterns": [],
  "failed_patterns": [],
  "blacklisted_operators": [],
  "blacklisted_fields": [],
  "submitted_alpha_formulas": [],
  "pairwise_log": []
}
```

After every session, you MUST update this file with what you learned.
This is how the system gets smarter over time.

---

# ══════════════════════════════════
# STEP 1 — FAILURE INTELLIGENCE SCAN
# ══════════════════════════════════
# READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
# ✅ STEP 1 COMPLETE — BLACKLIST BUILT
# ══════════════════════════════════

## YOUR TASK IN STEP 1:

1. Read ALL of these files if they exist:
   - `compile_error_report.md`
   - `compile_errors.md`
   - `compiler_errors.md`
   - `error_report.md`
   - `scratch/historical_scheduled_alphas.json`
   - `scratch/session_memory.json`

2. From every error file, extract and list:
   - Failed operators (e.g. `ts_delta` on raw event fields)
   - Failed field combinations
   - Failed dataset combinations
   - Failed syntax patterns
   - Failed timeline/delay structures
   - Failed neutralization usage
   - Failed division structures

3. Merge ALL failures into one **MASTER BLACKLIST**.

4. Print the Master Blacklist clearly:
```
MASTER BLACKLIST:
- [operator/pattern]: [reason it fails]
- [operator/pattern]: [reason it fails]
...
```

5. Also load `scratch/session_memory.json` and add its
   `blacklisted_operators` and `blacklisted_fields` to the Master Blacklist.

6. From `historical_scheduled_alphas.json`, extract all previously
   submitted formula strings. You will need these in Step 6 (Uniqueness).

## HARD COMPILER RULES — MEMORIZE THESE NOW:

| Rule | Description |
|------|-------------|
| VEC_AVG REQUIRED | All analyst4/analyst45 sparse fields MUST be wrapped in `vec_avg()` before any ts_ operator or rank() |
| NO RAW EVENT + SCALAR | Cannot do `event_field + 0.001` or `event_field - 0.01` |
| NO RAW EVENT / DAILY | Cannot divide event field by price or cap directly |
| BOOLEAN MUST USE TERNARY | `(close > open) ? value : other_value` — always parentheses |
| GROUP NAMES LOWERCASE | Use `subindustry` not `SUBINDUSTRY` inside formulas |
| WINDOW ≥ 2 INTEGER | All lookback windows must be positive integers ≥ 2 |
| STD/CORR WINDOW ≥ 5 | `ts_std_dev` and `ts_corr` need window ≥ 5 |
| NO NESTED RANK | No `rank(rank(x))` |
| NO BANNED OPERATORS | Never use `signed_power()`, `power()`, `log()`, `exp()` |
| TERNARY FALLBACK = SCALAR | `trade_when(cond, expr, 0)` — third arg must be 0 or 0.0 |
| SINGLE RANK ONLY | One rank level per formula max |
| TS_DELAY AWARENESS | Using `ts_delay(x,1)` with delay=1 setting = effective delay 2 |

✅ STEP 1 COMPLETE — BLACKLIST BUILT

---

# ══════════════════════════════════
# STEP 2 — LIVE DATASET FIELD DISCOVERY
# ══════════════════════════════════
# READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
# ✅ STEP 2 COMPLETE — ALL FIELDS DISCOVERED
# ══════════════════════════════════

## YOUR TASK IN STEP 2:

Read the actual dataset documentation files from disk.
DO NOT rely on any hardcoded field list. Discover everything fresh.

---

### FILES TO READ (read all that exist):
- `dataset.md`
- `documentation/dataset.md`
- `datasets/analyst4.md`
- `datasets/analyst14.md`
- `datasets/analyst45.md`
- `datasets/analyst44.md`
- Any other `datasets/*.md` files found in the workspace
- Any other `*.md` files that describe fields, schemas, or variables

If no dataset files exist, search for field names by scanning:
- Any `.json` files in `scratch/` for field name patterns
- Any previously submitted alpha formulas in `historical_scheduled_alphas.json`
  and extract all field names used — these are confirmed working fields

---

### FOR EACH DATASET FOUND, EXTRACT AND RECORD:

1. **Dataset name and prefix** (e.g. `anl4_`, `anl14_`, `anl45_`)
2. **Every available field name** — list ALL of them, no filtering
3. **Field type for each field:**
   - VECTOR (sparse/event-based) → requires `vec_avg()` wrapper
   - MATRIX (daily/continuous) → can be used directly in ts_ operators
4. **Update frequency** (daily, event-driven, quarterly, etc.)
5. **Any field-specific notes** (e.g. units, sparsity level, known gaps)

---

### HOW TO DETERMINE FIELD TYPE (if not documented):

| Signal | Likely Type |
|--------|-------------|
| Field name contains `estimate`, `forecast`, `revision`, `surprise` | VECTOR — use `vec_avg()` |
| Field name contains `mean_`, `consensus_`, `median_` with no event suffix | Check docs |
| Dataset is analyst4 or analyst45 | Assume VECTOR → use `vec_avg()` unless docs say otherwise |
| Dataset is analyst14 | Assume MATRIX → no wrapping needed unless docs say otherwise |
| Field updated on earnings dates or analyst report dates | VECTOR |
| Field updated every trading day without gaps | MATRIX |

**WHEN IN DOUBT → treat as VECTOR and use `vec_avg()`. Safe default.**

---

### DECAY RULES (apply based on field type, not dataset assumption):

| Field Type | Decay Setting |
|------------|--------------|
| VECTOR (sparse event fields) | `decay: 8` or `decay: 10` |
| MATRIX (daily continuous fields) | `decay: 5` or `decay: 6` |
| Cross-dataset hybrid (mixed types) | Use the SLOWER decay of the two |

---

### ALSO CHECK session_memory.json → `blacklisted_fields[]`
Remove any blacklisted fields from your discovered field list.
Do not use fields that previously caused compile errors.

---

### PRINT YOUR COMPLETE DISCOVERED FIELD INVENTORY:

```
FIELD DISCOVERY REPORT:
════════════════════════════════════════
Dataset: analyst4
  Type: VECTOR — vec_avg() required — decay 8-10
  Fields discovered: [N]
  Field list:
    - [field_name_1]: [description if available] — [VECTOR/MATRIX]
    - [field_name_2]: [description if available] — [VECTOR/MATRIX]
    ...

Dataset: analyst14
  Type: MATRIX — no wrapping needed — decay 5-6
  Fields discovered: [N]
  Field list:
    - [field_name_1]: [description if available] — [VECTOR/MATRIX]
    ...

Dataset: analyst45
  Type: VECTOR — vec_avg() required — decay 8
  Fields discovered: [N]
  Field list:
    - [field_name_1]: [description if available] — [VECTOR/MATRIX]
    ...

[Any additional datasets found]

TOTAL FIELDS AVAILABLE: [N]
BLACKLISTED FIELDS EXCLUDED: [N]
FIELDS READY FOR ALPHA GENERATION: [N]
════════════════════════════════════════
```

Use this full field list in Steps 3, 4, and 5.
More fields = more diversity = better alphas.

✅ STEP 2 COMPLETE — ALL FIELDS DISCOVERED

---

# ══════════════════════════════════
# STEP 3 — ACADEMIC ANOMALY RESEARCH
# ══════════════════════════════════
# READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
# ✅ STEP 3 COMPLETE — ANOMALY MAP BUILT
# ══════════════════════════════════

## YOUR TASK IN STEP 3:

Map every relevant market anomaly to the available datasets.
Every alpha you generate MUST be backed by one of these anomalies.
No anomaly = no alpha.

For each anomaly below, state:
- Which dataset(s) can capture it
- Which fields to use
- What the signal direction is (long high / short low)

---

### ANOMALY MAP:

| # | Anomaly | Description | Best Dataset | Signal Direction |
|---|---------|-------------|--------------|-----------------|
| 1 | **EPS Revision Momentum** | Stocks with rising EPS estimates outperform | analyst4, analyst14 | Long rising estimates |
| 2 | **Analyst Dispersion Premium** | Wide EBITDA high/low spread = more uncertainty = premium | analyst4 | Long high dispersion |
| 3 | **Post-Earnings Drift** | Stocks with high EPS surprise continue moving | analyst4 | Long positive surprise |
| 4 | **Consensus Herding** | When all analysts agree, contrarian signal | analyst4 | Short extreme consensus |
| 5 | **Analyst Conviction** | Analysts with high Jensen's alpha are more predictive | analyst45 | Long high Jensen's alpha |
| 6 | **Revenue Revision Signal** | Rising revenue estimates predict price | analyst14 | Long rising revenue |
| 7 | **Beta Timing** | Low beta stocks outperform in uncertain markets | analyst45 | Long low beta |
| 8 | **Absolute Return Performance** | Analysts who pick well historically → signal | analyst45 | Long high ad_ret_per |
| 9 | **FCF Surprise** | Free cash flow surprise vs expectation | analyst4 | Long high FCF estimate |
| 10 | **Pre-Tax Profit Spread** | Spread between PTP high/low = uncertainty | analyst4 | Long narrow spread recovery |
| 11 | **Cross-Dataset Conviction** | EPS revision + Jensen's alpha combo | analyst4 + analyst45 | Combined long |
| 12 | **Revenue/EPS Divergence** | When revenue rises but EPS doesn't → inefficiency | analyst14 | Long divergence |
| 13 | **Relative vs Absolute Analyst Return** | Stocks where rel return > abs return = alpha | analyst45 | Long rel > abs |
| 14 | **EBITDA Mean Momentum** | Trend in mean EBITDA estimate | analyst4 | Long rising trend |
| 15 | **Neglected Firm Effect** | Low analyst coverage → higher return | analyst4 | Long low coverage (low estimate count) |

## Also check `scratch/session_memory.json` → `successful_patterns[]`
Add any historically winning anomalies to your map with higher priority.

## Print the final anomaly assignments:
```
ANOMALY ASSIGNMENTS FOR THIS SESSION:
[List which anomalies you will target and which datasets]
```

✅ STEP 3 COMPLETE — ANOMALY MAP BUILT

---

# ══════════════════════════════════
# STEP 4 — DIVERSITY PLANNING MATRIX
# ══════════════════════════════════
# READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
# ✅ STEP 4 COMPLETE — DIVERSITY MATRIX CREATED
# ══════════════════════════════════

## YOUR TASK IN STEP 4:

Before writing a single formula, plan all NUM_ALPHAS alphas
in a diversity matrix. This prevents correlation and redundancy.

For each of the NUM_ALPHAS alphas, define:

| Alpha # | Dataset | Anomaly | Signal Type | Lookback | Decay | Key Fields | Expected Uniqueness |
|---------|---------|---------|-------------|----------|-------|------------|---------------------|
| 1 | ... | ... | ... | ... | ... | ... | ... |
| 2 | ... | ... | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... | ... | ... |

## DIVERSITY RULES FOR THE MATRIX:

- No two alphas can use the same field + same lookback combination
- Spread lookbacks across: 5, 8, 10, 12, 15, 20, 25, 30 days
- Use each dataset multiple times but vary fields and lookbacks
- Mix signal types: momentum, mean-reversion, revision, spread, hybrid
- At least 3 cross-dataset alphas (combining analyst4 + analyst45 or analyst14 + analyst45)
- At least 2 mean-reversion alphas
- At least 3 revision/delta-based alphas
- At least 2 dispersion/spread-based alphas

## Check `scratch/session_memory.json` → `pairwise_log[]`
Avoid lookback/field combinations that were highly correlated in past sessions.

## Print the complete matrix before proceeding.

✅ STEP 4 COMPLETE — DIVERSITY MATRIX CREATED

---

# ══════════════════════════════════
# STEP 5 — FORMULA GENERATION
# ══════════════════════════════════
# READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
# ✅ STEP 5 COMPLETE — RAW FORMULAS GENERATED
# ══════════════════════════════════

## YOUR TASK IN STEP 5:

Using the diversity matrix from Step 4, write the raw formula
for each alpha. Follow every compiler rule from Step 1.

For each alpha, generate 2-3 candidate formulas, then pick the best one.

---

## FORMULA TEMPLATES (Use as starting patterns, not copy-paste):

### Template A — EPS Revision Momentum (analyst4):
```
rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 10))
```

### Template B — EBITDA Dispersion Signal (analyst4):
```
rank(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high) 
     - vec_avg(anl4_fs_detail_estimates_advanced_af_nd_ebitda_low))
```

### Template C — Revenue Drift Momentum (analyst14):
```
rank(ts_delta(anl14_mean_revenue_fp1, 12))
```

### Template D — Jensen's Alpha Conviction (analyst45):
```
rank(vec_avg(anl45_jensensalpha))
```

### Template E — Cross-Dataset Hybrid (analyst4 + analyst45):
```
rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 8)) 
* rank(vec_avg(anl45_jensensalpha))
```

### Template F — Beta-Adjusted Signal (analyst45):
```
(rank(vec_avg(anl45_ad_rel_ret_per)) 
 - rank(vec_avg(anl45_beta))) / 2
```

### Template G — Volume-Gated Signal:
```
trade_when(
  volume > adv20 * 0.70,
  rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 15)),
  0
)
```

### Template H — Ternary Conditional Momentum:
```
(ts_delta(anl14_mean_eps_fp1, 10) > 0) 
  ? rank(ts_delta(anl14_mean_eps_fp1, 10)) 
  : -rank(ts_std_dev(anl14_mean_eps_fp1, 10))
```

### Template I — Correlation-Based Signal (analyst14):
```
rank(ts_corr(anl14_mean_eps_fp1, anl14_mean_revenue_fp1, 20))
```

### Template J — FCF vs EPS Cross-Ratio (analyst4):
```
rank(vec_avg(anl4_fs_detail_estimates_advanced_af_nd_fcf_high)) 
/ rank(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate))
```

---

## FORMULA CHECKLIST (apply to each candidate):

For every formula you write, confirm:
- [ ] All analyst4/analyst45 fields wrapped in `vec_avg()`
- [ ] No banned operators: `signed_power`, `power`, `log`, `exp`
- [ ] No raw event field + scalar arithmetic
- [ ] Boolean comparisons use `(expr) ? a : b` syntax
- [ ] All lookback windows are positive integers ≥ 2
- [ ] ts_std_dev / ts_corr windows ≥ 5
- [ ] No nested rank: `rank(rank(x))` is banned
- [ ] trade_when fallback is scalar 0 or 0.0
- [ ] group names in formula use lowercase: `subindustry`

## Output format for each alpha:
```
ALPHA [N]:
  Anomaly: [name]
  Dataset(s): [list]
  Candidate 1: [formula]
  Candidate 2: [formula]
  Candidate 3: [formula]
  SELECTED: [formula] — because [reason it's stronger]
```

✅ STEP 5 COMPLETE — RAW FORMULAS GENERATED

---

# ══════════════════════════════════
# STEP 6 — UNIQUENESS VALIDATION
# ══════════════════════════════════
# READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
# ✅ STEP 6 COMPLETE — UNIQUENESS VERIFIED
# ══════════════════════════════════

## YOUR TASK IN STEP 6:

Compare every selected formula from Step 5 against:
1. `historical_scheduled_alphas.json` — previously submitted formulas
2. `scratch/session_memory.json` → `submitted_alpha_formulas[]`
3. All other alphas in the current batch (self-check)

### UNIQUENESS RULES:

For each formula, check for:

| Check Type | Description |
|------------|-------------|
| **Exact match** | Identical formula string |
| **Near match** | Same fields + same operator + lookback ±2 days |
| **Structural match** | Same shape: `rank(ts_delta(vec_avg(X), N))` on same X |
| **Field match** | Same primary field used with any operator |

### SCORING:
- Exact match → HARD REJECT, generate new formula
- Near match → SOFT REJECT, change lookback by ≥5 or change operator
- Structural match → WARNING, change at least one design element
- No match → PASS ✅

### Output for each alpha:
```
ALPHA [N] UNIQUENESS CHECK:
  Vs historical: [PASS / REJECT — reason]
  Vs session batch: [PASS / REJECT — reason]
  Action: [ACCEPTED / REGENERATED — describe change if regenerated]
```

### After all checks, print final count:
```
UNIQUENESS SUMMARY:
  Total alphas: [N]
  Passed: [N]
  Regenerated: [N]
  All unique: YES / NO
```

If "All unique: NO" → go back and fix before proceeding.

✅ STEP 6 COMPLETE — UNIQUENESS VERIFIED

---

# ══════════════════════════════════
# STEP 7 — CORRELATION ESTIMATION
# ══════════════════════════════════
# READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
# ✅ STEP 7 COMPLETE — CORRELATION CHECK DONE
# ══════════════════════════════════

## YOUR TASK IN STEP 7:

Estimate pairwise correlation risk across all alphas in the batch.
Target: ALL pairs below MAX_PAIRWISE_CORR = 0.70

### CORRELATION RISK SCORING TABLE:

| Scenario | Estimated Correlation | Action |
|----------|-----------------------|--------|
| Same field, same lookback | 0.95+ | REDESIGN |
| Same field, lookback diff <5 | 0.80-0.90 | CHANGE LOOKBACK |
| Same field, lookback diff ≥8 | 0.60-0.75 | WARNING — add neutralization change |
| Same dataset, different fields | 0.40-0.65 | ACCEPTABLE |
| Different datasets, related anomaly | 0.30-0.55 | GOOD |
| Cross-dataset hybrid | 0.15-0.40 | BEST |
| Different anomaly, different dataset | 0.10-0.35 | EXCELLENT |

### For each pair of alphas, estimate and log:
```
CORRELATION MATRIX:
  Alpha 1 vs Alpha 2: [estimated corr] — [PASS / WARNING / REDESIGN]
  Alpha 1 vs Alpha 3: [estimated corr] — [PASS / WARNING / REDESIGN]
  ...
```

### Also check `scratch/session_memory.json` → `pairwise_log[]`
If a similar pair was historically high-correlation, treat as WARNING.

### Resolution for high-correlation pairs:
- Change the lookback window by ≥5 days
- Switch from momentum to mean-reversion direction
- Add volume gate via trade_when()
- Switch to cross-dataset hybrid version
- Change neutralization level (sector → subindustry or vice versa)

✅ STEP 7 COMPLETE — CORRELATION CHECK DONE

---

# ══════════════════════════════════
# STEP 8 — SETTINGS ASSIGNMENT & FINAL VALIDATION
# ══════════════════════════════════
# READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
# ✅ STEP 8 COMPLETE — ALL ALPHAS FINALIZED
# ══════════════════════════════════

## YOUR TASK IN STEP 8:

Assign the correct simulation settings to every alpha,
then run a final 12-point validation checklist on each one.

---

### SETTINGS RULES:

| Dataset Type | Decay Setting | Reason |
|-------------|---------------|--------|
| analyst4 (sparse event) | 8 or 10 | Avoid high turnover from sparse updates |
| analyst14 (daily matrix) | 5 or 6 | Can handle faster decay |
| analyst45 (sparse event) | 8 | Sparse conviction fields need slow decay |
| Cross-dataset hybrid | 8 | Use the slower of the two datasets |

### SETTINGS TEMPLATE:
```json
{
  "region": "USA",
  "delay": 1,
  "decay": [8 or 10 or 5 or 6 — based on dataset],
  "neutralization": "SUBINDUSTRY",
  "universe": "TOP3000",
  "truncation": 0.08
}
```

---

### FINAL 12-POINT VALIDATION CHECKLIST:

For EVERY alpha, confirm all 12 points:

```
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
```

If any alpha FAILS any of the 12 points → fix it before continuing.
Do NOT proceed to Step 9 with any failing alphas.

### Print final count:
```
VALIDATION SUMMARY:
  Total alphas validated: [N]
  All 12 checks passed: YES / NO
  Any regenerated in this step: YES / NO — [which ones]
```

✅ STEP 8 COMPLETE — ALL ALPHAS FINALIZED

---

# ══════════════════════════════════
# STEP 9 — SUBMISSION TO REVIEW BOX
# ══════════════════════════════════
# READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
# ✅ STEP 9 COMPLETE — ALL ALPHAS SUBMITTED
# ══════════════════════════════════

## YOUR TASK IN STEP 9:

Submit every validated alpha to the Review Box API.
Every alpha must be submitted. Count must match NUM_ALPHAS exactly.

---

### API DETAILS:
```
Endpoint: https://world-quant.onrender.com/api/queue-alpha
Method: POST
Headers:
  Authorization: Bearer yashthakreop
  Content-Type: application/json
```

### PAYLOAD FORMAT (one object per alpha):
```json
[
  {
    "family": "[anomaly family e.g. EPS_REVISION_MOMENTUM]",
    "dataset": "[dataset name e.g. analyst4]",
    "competition": "IQC2025",
    "hypothesis": "[one sentence economic rationale]",
    "anomaly_basis": "[academic anomaly name from Step 3]",
    "formula": "[the validated formula string]",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": [N],
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  }
]
```

### PRE-SUBMISSION COUNT VERIFICATION:
```
PRE-SUBMISSION CHECK:
  NUM_ALPHAS configured: [N]
  Alphas generated: [N]
  Alphas validated: [N]
  Alphas in payload: [N]
  All counts match: YES / NO
```

If any count mismatch → ABORT. Do not submit partial batches.

---

### SUBMISSION LOOP:

For each alpha, submit individually. Log every attempt:
```
SUBMITTING ALPHA [N]: [formula preview]
  HTTP Status: [200 / error code]
  Response: [response body]
  Result: SUCCESS ✅ / FAILED ❌
```

### ERROR HANDLING:
- HTTP 200 → Success, continue
- HTTP 4xx → Log error body, stop, do not retry blind
- HTTP 5xx → Log error, wait 30 seconds, retry once
- Connection error → Save all alphas to `scratch/failed_submission.json`, log failure

### FINAL SUBMISSION REPORT:
```
SUBMISSION REPORT:
  Total submitted: [N]
  Total succeeded: [N]
  Total failed: [N]
  Failed alpha indices: [list if any]
```

If total succeeded < NUM_ALPHAS → save unsent alphas to
`scratch/failed_submission.json` for retry next session.

### PYTHON SUBMISSION SCRIPT (run if API call fails from here):
```
C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe push_accepted_alphas.py --num-alphas [N]
```
Do NOT use `--dry-run` flag in production.

✅ STEP 9 COMPLETE — ALL ALPHAS SUBMITTED

---

# ══════════════════════════════════
# STEP 10 — SELF-IMPROVEMENT MEMORY UPDATE
# ══════════════════════════════════
# READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
# ✅ STEP 10 COMPLETE — MEMORY UPDATED. SESSION DONE.
# ══════════════════════════════════

## YOUR TASK IN STEP 10:

Update `scratch/session_memory.json` with everything learned
this session so the next run is smarter.

---

### UPDATE THESE FIELDS:

```json
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
```

---

### SELF-IMPROVEMENT REFLECTION:

Answer these 5 questions and save answers in `session_notes`:

1. **What worked well this session?**
   (Which anomalies / fields / lookbacks produced the cleanest signals?)

2. **What failed and why?**
   (Which formulas were rejected or had compilation issues?)

3. **What should be tried next session?**
   (New anomaly combinations, unexplored fields, different lookbacks?)

4. **What was the most unique alpha this session?**
   (The one least correlated with historical — describe it)

5. **What improvement would raise Sharpe most next session?**
   (Based on what you know about the data now)

---

### FINAL SESSION SUMMARY:
```
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
```

✅ STEP 10 COMPLETE — MEMORY UPDATED. SESSION DONE.

---

# ═══════════════════════════════════════════════════════════════
# EXECUTION REMINDER
# ═══════════════════════════════════════════════════════════════
#
# YOU MUST:
# 1. Execute steps ONE AT A TIME in order
# 2. Print "✅ STEP [N] COMPLETE" after each step
# 3. Never skip a step
# 4. Never combine steps
# 5. Never look ahead to the next step while in the current step
# 6. Update session_memory.json at Step 10 — ALWAYS
#
# THE GOAL IS NOT SPEED. THE GOAL IS QUALITY AND CONSISTENCY.
# A SYSTEM THAT IMPROVES EVERY 10 MINUTES IS BETTER THAN
# ONE THAT GENERATES RANDOM ALPHAS INSTANTLY.
# ═══════════════════════════════════════════════════════════════

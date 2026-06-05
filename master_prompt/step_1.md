SESSION CONFIG (READ THIS FIRST — ALWAYS)
```json
{
  "NUM_ALPHAS": 40,
  "DATASETS": [
    "analyst14", "analyst16", "analyst4", "analyst44", "analyst45", "analyst69", "analyst7", "earnings7",
    "fundamental6", "insiders1", "macro10", "macro27", "macro38",
    "model109", "model135", "shortinterest7", "model26",
    "news12", "news17", "news18", "news21", "news3", "news31", "news36", "news38", "news46", "news48", "news5", "news50", "news59", "news7", "news76", "news94",
    "option8", "pv103", "pv104", "pv13", "pv141", "pv53", "pv63", "pv98", "risk60"
  ],
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
Before Step 1, read scratch/session_memory.json if it exists. It contains:
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

After every session, you MUST update this file with what you learned. This is how the system gets smarter over time.

══════════════════════════════════
STEP 1 — FAILURE INTELLIGENCE SCAN
══════════════════════════════════
READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
✅ STEP 1 COMPLETE — BLACKLIST BUILT
══════════════════════════════════

## YOUR TASK IN STEP 1:
Read ALL of these files if they exist:
- compile_error_report.md
- compile_errors.md
- compiler_errors.md
- error_report.md
- scratch/historical_scheduled_alphas.json
- scratch/session_memory.json

From every error file, extract and list:
- Failed operators (e.g. ts_delta on raw event fields)
- Failed field combinations
- Failed dataset combinations
- Failed syntax patterns
- Failed timeline/delay structures
- Failed neutralization usage
- Failed division structures

Merge ALL failures into one MASTER BLACKLIST.

Print the Master Blacklist clearly:
```
MASTER BLACKLIST:
- [operator/pattern]: [reason it fails]
- [operator/pattern]: [reason it fails]
...
```

Also load scratch/session_memory.json and add its blacklisted_operators and blacklisted_fields to the Master Blacklist.

From historical_scheduled_alphas.json, extract all previously submitted formula strings. You will need these in Step 6 (Uniqueness).

## HARD COMPILER RULES — MEMORIZE THESE NOW:
| Rule | Description |
|---|---|
| VEC_AVG REQUIRED | All analyst4/analyst45 sparse fields MUST be wrapped in vec_avg() before any ts_ operator or rank() |
| NO RAW EVENT + SCALAR | Cannot do event_field + 0.001 or event_field - 0.01 |
| NO RAW EVENT / DAILY | Cannot divide event field by price or cap directly |
| BOOLEAN MUST USE TERNARY | (close > open) ? value : other_value — always parentheses |
| GROUP NAMES LOWERCASE | Use subindustry not SUBINDUSTRY inside formulas |
| WINDOW ≥ 2 INTEGER | All lookback windows must be positive integers ≥ 2 |
| STD/CORR WINDOW ≥ 5 | ts_std_dev and ts_corr need window ≥ 5 |
| NO NESTED RANK | No rank(rank(x)) |
| NO BANNED OPERATORS | Never use signed_power(), power(), log(), exp() |
| TERNARY FALLBACK = SCALAR | trade_when(cond, expr, 0) — third arg must be 0 or 0.0 |
| SINGLE RANK ONLY | One rank level per formula max |
| TS_DELAY AWARENESS | Using ts_delay(x,1) with delay=1 setting = effective delay 2 |

✅ STEP 1 COMPLETE — BLACKLIST BUILT

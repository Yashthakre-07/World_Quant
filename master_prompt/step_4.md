step 4

✅ STEP 4 COMPLETE — DIVERSITY MATRIX CREATED
══════════════════════════════════
YOUR TASK IN STEP 4:
Before writing a single formula, plan all NUM_ALPHAS alphas in a diversity matrix. This prevents correlation and redundancy.

For each of the NUM_ALPHAS alphas, define:

Alpha #	Dataset	Anomaly	Signal Type	Lookback	Decay	Key Fields	Expected Uniqueness
1	...	...	...	...	...	...	...
2	...	...	...	...	...	...	...
...	...	...	...	...	...	...	...
DIVERSITY RULES FOR THE MATRIX:
No two alphas can use the same field + same lookback combination
Spread lookbacks across: 5, 8, 10, 12, 15, 20, 25, 30 days
Utilize multiple datasets from all 5 thematic categories (Analyst, Fundamental/Macro, Technical Models, News Sentiment, Options/PV)
Mix signal types: momentum, mean-reversion, revision, spread, hybrid, sentiment-based, volatility-based
At least 3 cross-dataset alphas (combining analyst + news/sentiment or fundamental + technical models)
At least 2 mean-reversion alphas
At least 3 revision/delta-based alphas
At least 2 dispersion/spread-based alphas
Check scratch/session_memory.json → pairwise_log[]
Avoid lookback/field combinations that were highly correlated in past sessions.

Print the complete matrix before proceeding.
✅ STEP 4 COMPLETE — DIVERSITY MATRIX CREATED

══════════════════════════════════

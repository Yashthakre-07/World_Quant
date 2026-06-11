step 3

STEP 3 — ACADEMIC ANOMALY RESEARCH
══════════════════════════════════
READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
✅ STEP 3 COMPLETE — ANOMALY MAP BUILT
══════════════════════════════════
YOUR TASK IN STEP 3:
Map every relevant market anomaly to the available datasets. Every alpha you generate MUST be backed by one of these anomalies. No anomaly = no alpha. Ensure your mapping spans across all categories of the 42 thematic datasets listed in [theme_Dataset.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/theme_Dataset.md) (Analyst Consensus, Fundamental, Macro, Technical Factor Models, News Sentiment, and Options/PV).

For each anomaly below, state:

Which dataset(s) can capture it
Which fields to use
What the signal direction is (long high / short low)
ANOMALY MAP:
#	Anomaly	Description	Best Dataset	Signal Direction
1	EPS Revision Momentum	Stocks with rising EPS estimates outperform	analyst4, analyst14	Long rising estimates
2	Analyst Dispersion Premium	Wide EBITDA high/low spread = more uncertainty = premium	analyst4	Long high dispersion
3	Post-Earnings Drift	Stocks with high EPS surprise continue moving	analyst4	Long positive surprise
4	Consensus Herding	When all analysts agree, contrarian signal	analyst4	Short extreme consensus
5	Analyst Conviction	Analysts with high Jensen's alpha are more predictive	analyst45	Long high Jensen's alpha
6	Revenue Revision Signal	Rising revenue estimates predict price	analyst14	Long rising revenue
7	Beta Timing	Low beta stocks outperform in uncertain markets	analyst45	Long low beta
8	Absolute Return Performance	Analysts who pick well historically → signal	analyst45	Long high ad_ret_per
9	FCF Surprise	Free cash flow surprise vs expectation	analyst4	Long high FCF estimate
10	Pre-Tax Profit Spread	Spread between PTP high/low = uncertainty	analyst4	Long narrow spread recovery
11	Cross-Dataset Conviction	EPS revision + Jensen's alpha combo	analyst4 + analyst45	Combined long
12	Revenue/EPS Divergence	When revenue rises but EPS doesn't → inefficiency	analyst14	Long divergence
13	Relative vs Absolute Analyst Return	Stocks where rel return > abs return = alpha	analyst45	Long rel > abs
14	EBITDA Mean Momentum	Trend in mean EBITDA estimate	analyst4	Long rising trend
15	Neglected Firm Effect	Low analyst coverage → higher return	analyst4	Long low coverage (low estimate count)
Also check scratch/session_memory.json → successful_patterns[]
Add any historically winning anomalies to your map with higher priority.

Print the final anomaly assignments:

ANOMALY ASSIGNMENTS FOR THIS SESSION:
[List which anomalies you will target and which datasets]
✅ STEP 3 COMPLETE — ANOMALY MAP BUILT

══════════════════════════════════

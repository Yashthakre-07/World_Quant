# 10 Steps to Start on BRAIN

Getting started on WorldQuant BRAIN can feel overwhelming due to the massive volume of datasets and mathematical operators. Follow this structured, step-by-step checklist to systematically build and submit your first alpha.

---

## The Step-by-Step Path to Your First Submission

### Step 1: Create and Verify Your Account
*   Sign up at the [WorldQuant BRAIN](https://worldquant.com/brain) platform. Complete your profile, verify your email, and accept the platform’s Terms of Use.

### Step 2: Complete the Platform Onboarding Tutorials
*   Navigate to the platform's **Help** or **Documentation** tab. Read the introductory articles and view their video tutorials. Completing these will grant you basic familiarity with the web simulator interface.

### Step 3: Explore the Data Explorer
*   Open the **Data Explorer** tool. Search for simple, high-coverage market datasets.
*   **Recommendation**: Start with standard equity fields like `close` (daily closing price), `open` (opening price), `volume` (trading volume), or `vwap` (volume-weighted average price).

### Step 4: Pick a Financial Hypothesis
*   Formulate a simple market theory.
*   *Example Hypothesis (Price Reversion)*: "Stocks that close lower than where most volume traded today (the VWAP) have been pushed down artificially and will tend to revert upwards tomorrow."

### Step 5: Translate Your Idea into FastExpression
*   Write your hypothesis as a formula.
*   *Formula*: `vwap - close`
*   *Enhancement*: To avoid concentrated weights on high-priced stocks, cross-sectionally rank the variables: `rank(vwap) - rank(close)`.

### Step 6: Configure Your Simulation Settings
*   Open the simulation configuration panel. Set these industry-standard settings:
    *   **Universe**: `TOP3000` (Broad, liquid US stock universe).
    *   **Neutralization**: `SUBINDUSTRY` (Removes sector and subindustry risk).
    *   **Decay**: `6` (Smooths position weights to limit turnover).
    *   **Delay**: `1` (Trades tomorrow based on today's signals).

### Step 7: Run Your First Backtest Simulation
*   Click the **Simulate** button. Wait for 30–60 seconds as the platform runs your expression through 20+ years of historical data.

### Step 8: Analyze the Simulation Output
*   Check the generated report:
    *   *Sharpe Ratio*: Is it $\ge 1.25$?
    *   *Turnover*: Is it between $1\%$ and $70\%$?
    *   *Fitness*: Is it $\ge 1.0$?
    *   *Weight Checks*: Did it pass `CONCENTRATED_WEIGHT`?

### Step 9: Optimize and Polish Your Formula
*   If your alpha fails due to borderline metrics, tune it:
    *   If **Turnover** is too high ($>60\%$): Increase `decay` to `10` or `12`.
    *   If **Sharpe** is too low ($<1.25$): Change neutralization to `SUBINDUSTRY` or add a time-series delay to look at multi-day changes: `rank(ts_delay(close, 3)) - rank(close)`.

### Step 10: Submit Your Alpha for Forward Testing
*   Once all metrics are green, click the **Submit** button. Your alpha will enter the 6-week **Out-of-Sample (OOS)** period. If it performs well, you earn points and move closer to becoming a paid research consultant!

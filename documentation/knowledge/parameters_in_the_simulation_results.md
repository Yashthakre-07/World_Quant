# Parameters in the Simulation Results

When a backtest finishes executing on WorldQuant BRAIN, the engine returns a detailed results payload. Understanding every performance and risk parameter in this payload is critical for diagnosing and optimizing your trading signal.

---

## 1. Key Performance Output Parameters

*   **Sharpe (Sharpe Ratio)**:
    *   The primary metric for risk-adjusted return. An annualized Sharpe of $1.50+$ is the baseline target.
*   **Fitness**:
    *   The composite metric scoring returns, risk (Sharpe), and trading cost efficiency (Turnover). Must be $\ge 1.0$ for submission.
*   **Turnover**:
    *   The annualized portfolio turnover percentage. Measures how quickly weights are rebalanced daily. Lower is preferred to control transaction costs.
*   **Returns (Annualized Returns)**:
    *   The total percentage return the portfolio generated over a year, before transaction fees. High returns are good, but only if they are achieved without excessive volatility.
*   **Drawdown (Max Drawdown)**:
    *   The deepest percentage drop from a historic portfolio peak. It is a critical metric for assessing real-world capital loss risk. Keep this below $15\%$.

---

## 2. Advanced Diagnostic Parameters

*   **Information Coefficient (IC / Rank IC)**:
    *   Measures the correlation between your signal values and the subsequent actual stock returns. A positive, stable Rank IC (typically $> 0.02$) proves your formula has genuine predictive signal rather than being random.
*   **Margin (Returns / Turnover)**:
    *   A ratio that determines if the alpha is profitable after accounting for trading costs.
    *   **Interpretation**: If margin is low, transaction fees will consume all profits. A healthy margin is $> 1.50$.
*   **Long-Only / Short-Only Metrics**:
    *   Shows the Sharpe and returns of only the long positions and only the short positions.
    *   **Tuning Tip**: If your long-only Sharpe is high but short-only is negative, your signal is heavily biased. You may need to apply stricter group mean-centering (`group_neutralize`) to balance the longs and shorts.

---

## 3. Sub-Universe Verification Vectors

The result payload includes metric breakdowns for different segments of the stock universe:
*   **Large-Cap Sharpe / Liquid Sharpe**:
    *   Verifies that the alpha generates healthy signal on the largest, most liquid companies. If these sub-universe Sharpes are negative, the alpha fails the safety check, as it indicates the model only works on risky, illiquid stocks.
*   **Year-by-Year Sharpe**:
    *   Shows the Sharpe ratio for each individual calendar year in the simulation history.
    *   **Rule**: The year-by-year Sharpe must be stable. If an alpha has a Sharpe of $4.0$ in 2020 but is negative in 2018, 2019, 2021, and 2022, it is a highly unstable "regime-specific" alpha and will be rejected.

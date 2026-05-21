# Performance Metrics and Submission Rules

To qualify for production submission on the WorldQuant Brain platform, simulated alphas must pass strict mathematical and behavioral benchmarks. Alphas that do not satisfy these targets receive a `SOFT_FAIL` or `HARD_REJECT` status.

---

## 1. Core Platform Metrics

### A. Sharpe Ratio
The **Sharpe Ratio** measures risk-adjusted return. It quantifies how much excess return the portfolio generates per unit of portfolio volatility.
*   **Target**: $\ge 1.25$ (Platform cutoff), $> 2.0$ (Ideal/Excellent).
*   **Math Formulation**:
    $$\text{Sharpe} = \sqrt{252} \times \frac{\mu_{\text{daily\_PnL}}}{\sigma_{\text{daily\_PnL}}}$$
    *(where 252 represents the standard number of trading business days per year).*

### B. Fitness
**Fitness** is a composite metric that rewards alphas that maintain strong risk-adjusted returns (Sharpe) while minimizing transaction drag (Turnover).
*   **Target**: $\ge 1.0$ (Cutoff for successful production submission).
*   **Math Formulation**:
    $$\text{Fitness} = \text{Sharpe} \times \sqrt{\frac{|\text{Annualized Returns}|}{\max(\text{Turnover}, 0.125)}}$$
*   **Implication**: If an alpha has high Sharpe but extremely high Turnover (e.g. 80%), its Fitness will drop below 1.0. Lowering turnover via decay is the primary mechanism to fix Fitness failures.

### C. Turnover
**Turnover** measures daily trading volume relative to the portfolio's book size. High turnover triggers transaction costs that would erode the alpha's live profitability.
*   **Target**: $\le 70.0\%$ (Strict platform cutoff), $< 30\%$ (Preferred).
*   **Math Formulation**:
    $$\text{Turnover} = \frac{\sum |w_{i,t} - w_{i,t-1} \cdot (1 + r_{i,t})|}{\text{Portfolio Book Size}}$$

---

## 2. Compliance and Self-Correlation Rules

Even if an alpha passes the metrics thresholds, it must satisfy the following checks to be submittable:

1.  **Concentrated Weight Check (`CONCENTRATED_WEIGHT`)**
    *   **Rule**: The portfolio weight allocated to any single instrument cannot exceed a safe threshold (generally dictated by liquidity).
    *   **Failure Trigger**: Often caused by math scale issues (like the raw `scale()` operator acting on outliers) or overly concentrated portfolio weights.
    *   **Resolution**: Use cross-sectional percentiles (`rank`), z-scores (`zscore`), or winsorization (`pasteurize`) to smooth allocations across the entire universe.

2.  **Low Sub-Universe Sharpe (`LOW_SUB_UNIVERSE_SHARPE`)**
    *   **Rule**: The alpha must show positive risk-adjusted performance when simulated on subsets of the universe (e.g., highly liquid or large-cap equities).
    *   **Resolution**: Avoid over-indexing on micro-cap or illiquid stocks by using liquid price signals (`vwap`) or neutralizing against the broad market.

3.  **Self-Correlation (`SELF_CORRELATION`)**
    *   **Rule**: The submitted alpha must not be highly correlated with any of your previously submitted or accepted alphas.
    *   **Threshold**: Correlation of daily PnL vectors must be $< 0.70$.

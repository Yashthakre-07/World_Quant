# Intermediate Pack: Understand Results [1/2]

Once you run a simulation on WorldQuant BRAIN, the engine generates a complex set of performance metrics. Understanding these numbers is the difference between a random guesser and a professional quantitative researcher.

---

## 1. The Core Performance Metrics

Your simulation results are measured along three primary axes: return quality, transaction cost impact, and risk exposure.

### A. Sharpe Ratio (The Quality Metric)
*   **What it measures**: Risk-adjusted excess return. It represents how much return your strategy generates for every unit of volatility/risk.
*   **Formula**:
    $$\text{Sharpe} = \sqrt{252} \times \frac{\mu_{\text{daily\_PnL}}}{\sigma_{\text{daily\_PnL}}}$$
*   **Target**: The platform requires a minimum of **$1.25$** for production submission, but a Sharpe above **$1.50$** is ideal, and above **$2.0$** is outstanding.

### B. Turnover (The Sizing/Cost Metric)
*   **What it measures**: How frequently the portfolio changes its stock positions. Daily turnover is calculated as the total dollar value of shares bought and sold, divided by the total value of the portfolio.
*   **Target**: Must be strictly between **$1.0\%$ and $70.0\%$**. 
*   **Why it matters**: A turnover of $80\%$ means you are replacing $80\%$ of your portfolio every single day. In live trading, this creates massive transaction costs and execution slippage that will completely wipe out your profits.

### C. Fitness (The Combined Efficiency Score)
*   **What it measures**: The efficiency of the alpha, balancing risk-adjusted return (Sharpe) and annualized return against the penalty of transaction costs (Turnover).
*   **Formula**:
    $$\text{Fitness} = \text{Sharpe} \times \sqrt{\frac{|\text{Annualized Returns}|}{\max(\text{Turnover}, 0.125)}}$$
*   **Target**: Must be **$\ge 1.0$** for successful submission.
*   **Implication**: If your Sharpe is high (e.g. $1.8$) but your turnover is also high (e.g. $65\%$), your Fitness will be dragged down and may fail to reach $1.0$. Managing turnover is the primary key to achieving high Fitness scores.

---

## 2. Advanced Risk Metrics

To thoroughly understand your results, monitor these secondary metrics:

*   **Drawdown (Max Drawdown)**:
    *   The largest peak-to-trough drop in the portfolio's cumulative value over the simulation window.
    *   **Ideal**: Max drawdown should be kept as low as possible. A drawdown exceeding $20\%$ is a red flag indicating high regime risk.
*   **Margin (Returns over Turnover)**:
    *   Represents the expected payout per dollar traded.
    *   $$\text{Margin} = \frac{\text{Annualized Returns}}{\text{Annualized Turnover}}$$
    *   High margin signals that the alpha can absorb transaction costs without going negative.
*   **Information Coefficient (IC / Rank IC)**:
    *   Measures the correlation between your alpha's predictions and actual future returns. A Rank IC above $0.02$ indicates strong predictive power.

---

## 3. Classifying the Simulation Status

After a simulation is run, the engine classifies the result:
*   **SUBMITTED (Submittable)**: Passed all thresholds! Sharpe $\ge 1.25$, Fitness $\ge 1.0$, Turnover between $1\%$ and $70\%$, and weight checks passed.
*   **SOFT_FAIL**: Borderline results (e.g., Sharpe is $1.3$ but Fitness is $0.92$). Good candidate for minor parameter adjustments (tuning decay, scale, or neutralization).
*   **HARD_REJECT**: Sharpe is below $1.0$ or turnover is outside boundaries. Discard or majorly rewrite.
*   **ERROR**: FastExpression syntax error, invalid field, or mathematical runtime exception (like dividing by zero).

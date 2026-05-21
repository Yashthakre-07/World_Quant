# WorldQuant BRAIN Starter Pack: Read This First

Welcome to the WorldQuant BRAIN platform! This starter pack serves as your comprehensive entry guide, designed to accelerate your journey from registering on the platform to successfully submitting high-scoring, production-grade formulaic alphas. 

---

## 1. What is WorldQuant BRAIN?
WorldQuant BRAIN is a web-based, crowdsourced quantitative research platform. It allows global researchers to build, backtest, and submit formulaic trading signals (called **Alphas**) using WorldQuant’s proprietary datasets and high-performance simulation infrastructure. 

Outstanding contributors can qualify to become **Research Consultants**, enabling them to earn performance-based payouts by generating high-quality alphas that get accepted into WorldQuant's production portfolio.

---

## 2. Core Concepts of Alpha Design

An **Alpha** is a mathematical model or formula that predicts the relative future performance of financial instruments (typically liquid equities).
*   **Formulaic Representation**: Written in a vectorized proprietary language called **FastExpression** (e.g., `-ts_delta(close, 5)`).
*   **Cross-Sectional Portfolio**: At any point in time, the simulator evaluates the formula for every stock in the active universe, yielding a numerical score for each stock.
*   **Long-Short Weights**: These scores are converted into portfolio weights. Stocks with the highest relative scores receive long (positive) weights, and stocks with the lowest relative scores receive short (negative) weights. The total weights are normalized so the portfolio is market-neutral (sum of longs = sum of shorts).

---

## 3. The 6-Step Workflow

1.  **Ideation & Hypothesis**: Formulate a financial reason why a stock should go up or down (e.g., "Stocks with unusually high volume spikes tend to revert in price").
2.  **Dataset Selection**: Discover fields in the **Data Explorer** that represent your variables (e.g., `volume`, `vwap`, `close`).
3.  **FASTEXPR Implementation**: Translate the hypothesis into a mathematical expression using FASTEXPR operators (e.g., `trade_when(ts_std(returns, 20) > 0.02, -ts_delta(close, 5), 0)`).
4.  **Simulation Configuration**: Select parameters like the target universe (e.g., `TOP3000`), neutralization (e.g., `SUBINDUSTRY`), and decay (e.g., `6` or `10`).
5.  **Simulation & Evaluation**: Submit the simulation. Within 30–90 seconds, check the risk-adjusted results (Sharpe Ratio, Fitness, and Turnover).
6.  **Submission & Forward Testing**: If the alpha satisfies platform criteria, submit it. It enters a 6-week forward-testing period (Out-of-Sample) to verify robustness.

---

## 4. Key Metrics to Master

To pass platform tests, your alpha must satisfy strict numeric thresholds:
*   **Sharpe Ratio ($\ge 1.25$ cutoff, $> 1.50$ target)**: Risk-adjusted return metric. Measures excess returns relative to volatility.
*   **Fitness ($\ge 1.00$ cutoff)**: A compound metric defined as:
    $$\text{Fitness} = \text{Sharpe} \times \sqrt{\frac{|\text{Annualized Returns}|}{\max(\text{Turnover}, 0.125)}}$$
*   **Turnover ($1.0\% \text{ to } 70.0\%$ allowed, $< 40.0\%$ target)**: Measures the average percentage of the portfolio's book value that is rebalanced/traded daily. High turnover erodes returns via transaction costs.

---

## 5. Critical Tips for Success
*   **Never Overfit**: Do not stack operators endlessly just to improve the historical Sharpe ratio. Overfitted alphas fail forward-testing immediately.
*   **Use Decay Strategically**: If your alpha's **Turnover** is too high, increase the `decay` setting (e.g. from `6` to `10` or `12`) to smooth out daily weight changes.
*   **Understand Neutralization**: Neutralizing at the `SUBINDUSTRY` level strips away industry-specific market risk, which frequently boosts risk-adjusted Sharpe ratios.

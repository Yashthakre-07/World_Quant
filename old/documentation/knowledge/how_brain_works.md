# How BRAIN Works

WorldQuant BRAIN is a sophisticated simulation platform that evaluates mathematical ideas and translates them into simulated quantitative investment portfolios. To build high-quality alphas, it is crucial to understand the engine’s internal mechanics.

---

## 1. The Cross-Sectional Allocation Engine

At its core, WorldQuant BRAIN operates on a **cross-sectional** basis. Rather than asking "Is stock A going up?", the simulator asks "Which stocks in my universe will outperform the others tomorrow?"

1.  **Daily Expression Evaluation**: Every single business day, the engine takes your FastExpression and evaluates it for every stock in the active universe (e.g. `TOP3000`).
2.  **Raw Signal Matrix**: This produces a vector of daily scores. If stock $i$ has a higher score than stock $j$, your alpha is predicting that stock $i$ will outperform stock $j$.
3.  **Signal Normalization**: The engine automatically strips away absolute values. It subtracts the mean of the scores to center them around zero (long-short neutrality) and scales them so that the total absolute leverage equals $1.0$.

---

## 2. Daily Portfolio Rebalancing

Once daily weights are calculated, the engine simulates trading:
*   **Executing Trades**: If Stock A's weight changes from $+0.5\%$ yesterday to $+0.8\%$ today, the simulator "buys" an additional $0.3\%$ of the portfolio's book size of Stock A at the market open (using Delay 1).
*   **Transaction Costs**: The simulator models realistic transaction costs and market impact. The cost is proportional to the daily **Turnover**. If your alpha trades excessively, these modeled transaction costs are subtracted from the simulated PnL, severely degrading the Sharpe and Fitness metrics.

---

## 3. Risk Neutralization Under the Hood

When you select a neutralization level (e.g., `SUBINDUSTRY`):
1.  The engine groups the stocks into their respective industry classifications (using GICS or similar standards).
2.  For each group, it calculates the average weight.
3.  It subtracts this group average weight from each stock's weight, ensuring that the net weight of every sector or subindustry is exactly **zero**.
4.  **The Result**: The portfolio has zero exposure to broad industry trends. If Tech stocks crash but your Tech alphas are industry-neutral, the alpha will not lose money, because its long Tech positions are perfectly hedged by its short Tech positions. It only gains or loses money based on which *individual* Tech stocks did better or worse than the others.

---

## 4. The Aggregate Performance Aggregation

WorldQuant evaluates your complete submitted portfolio as a whole:
*   **Correlation Penalty**: If you submit 10 alphas that all rely on similar price reversion formulas, their returns will be highly correlated. The engine penalizes this because it does not provide diversification.
*   **Diversification Reward**: A collection of 10 diverse, moderately-performing alphas (e.g. some fundamental, some price-based, some sentiment) is far more valuable than a single high-performing alpha, as their uncorrelated returns smooth out the overall PnL curve.

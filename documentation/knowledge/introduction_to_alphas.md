# Introduction to Alphas

In quantitative finance, an **Alpha** refers to an investment strategy’s ability to beat the market, or the active return on an investment relative to a market benchmark. On WorldQuant BRAIN, an alpha is formulated as a mathematical expression that outputs daily portfolio weights for a universe of stocks.

---

## 1. The Anatomy of a Formulaic Alpha

A formulaic alpha is a single mathematical function that processes historical market, fundamental, or alternative data to produce predictive signals. 
*   **Vector Inputs**: Time-series matrices of asset features (e.g., closing prices, volume, earnings per share).
*   **Vector Outputs**: A real number for every stock in the asset universe. For a universe of $N$ stocks, the formula generates $N$ raw scores:
    $$\mathbf{s}_t = [s_{1,t}, s_{2,t}, \dots, s_{N,t}]$$

---

## 2. Converting Signals to Portfolio Weights

The simulation engine automatically transforms the raw score vector $\mathbf{s}_t$ into tradeable portfolio weights $\mathbf{w}_t$ through several processing steps:

### A. Cross-Sectional Ranking / Standardization
To remove absolute scale and outliers, raw signals are often cross-sectionally ranked or standard-scored (z-scored):
$$\text{zscore}(s_{i,t}) = \frac{s_{i,t} - \mu(\mathbf{s}_t)}{\sigma(\mathbf{s}_t)}$$

### B. Mean Centering (Market Neutrality)
To ensure the alpha is market-neutral (i.e. does not gain or lose money purely from general market movements), the weights are mean-centered so that the sum of all long positions exactly equals the sum of all short positions:
$$\sum_{i=1}^{N} w_{i,t} = 0$$

### C. Scaling
The resulting weight vectors are scaled such that the sum of the absolute weights equals $1.0$ (or $100\%$ leverage):
$$\sum_{i=1}^{N} |w_{i,t}| = 1.0$$
This guarantees that the alpha maintains a stable book size and constant leverage.

---

## 3. Key Alpha Classifications

*   **Reversion (Mean Reverting)**:
    *   **Hypothesis**: Extreme price movements away from historical means will revert.
    *   **Syntax Pattern**: `-ts_delta(close, d)` or `-group_zscore(close, industry)`.
*   **Momentum (Trend Following)**:
    *   **Hypothesis**: Strong performance over a medium horizon (e.g. 1–3 months) will continue.
    *   **Syntax Pattern**: `ts_delta(close, 20)` or `ts_regression(returns, close, 20)`.
*   **Value (Fundamental)**:
    *   **Hypothesis**: Undervalued firms based on ratios outperform overvalued ones.
    *   **Syntax Pattern**: `-rank(enterprise_value / ebitda)`.
*   **Alternative / Sentiment**:
    *   **Hypothesis**: Social media buzz or news sentiment flows predict short-term stock shifts.
    *   **Syntax Pattern**: `ts_decay_linear(news_sentiment, 5)`.

---

## 4. Golden Rules of Alpha Research

1.  **Start with a hypothesis**: Do not write random expressions. State the economic rationale *first*.
2.  **Ensure structural diversity**: If your alpha correlates heavily with existing ideas ($>0.70$ correlation), it adds no value. Look for unique dataset combinations.
3.  **Respect trading limits**: Make sure your alpha is tradeable. High-turnover strategies look great in backtests but lose all profits to transaction costs in production.

# Alpha Examples for Beginners

To help you get started, here are several classic quantitative trading signal templates written in FastExpression. These examples cover different financial themes and illustrate standard syntax patterns.

---

## 1. Simple Price Reversion (Mean Reversion)
*   **Hypothesis**: Stocks that closed near their daily low price today have been oversold and will likely bounce back tomorrow.
*   **Formula**:
    ```text
    -rank(close - low) / rank(high - low)
    ```
*   **Why it works**: Captures short-term overextensions. The minus sign (`-`) inverts the rank, meaning we go long on stocks that closed closest to their daily low.
*   **Recommended Settings**:
    *   Neutralization: `SUBINDUSTRY`
    *   Decay: `6` to `8`

---

## 2. Volatility-Gated Price Reversion
*   **Hypothesis**: Price reversion is strongest during high-market-volatility regimes. We only trade when historical volatility is high.
*   **Formula**:
    ```text
    trade_when(ts_rank(ts_std_dev(returns, 20), 252) > 0.6, -ts_delta(close, 5), 0)
    ```
*   **Why it works**: The `trade_when` operator restricts trading weights to `0` unless the stock's rolling $20$-day standard deviation of returns is in the top $40\%$ of its own annual range. This reduces turnover by ignoring quiet market conditions.
*   **Recommended Settings**:
    *   Neutralization: `SUBINDUSTRY`
    *   Decay: `8`

---

## 3. Fundamental Value Alpha
*   **Hypothesis**: Cheap, profitable companies (low Enterprise Value to EBITDA) outperform expensive companies over medium-to-long horizons.
*   **Formula**:
    ```text
    -group_neutralize(rank(enterprise_value / ebitda), subindustry)
    ```
*   **Why it works**: Classic value investing. Using `group_neutralize` with `subindustry` ensures we compare tech companies to tech companies, and banks to banks, preventing sector biases. Since fundamental quarterly data changes slowly, this naturally has low turnover.
*   **Recommended Settings**:
    *   Neutralization: `INDUSTRY`
    *   Decay: `15` to `20` (High decay to match the slow fundamental updates)

---

## 4. Volume-Weighted Momentum
*   **Hypothesis**: Price trends that are accompanied by high trading volume are stronger and more sustainable.
*   **Formula**:
    ```text
    ts_decay_linear(rank(ts_delta(close, 10)) * rank(ts_mean(volume, 5)), 10)
    ```
*   **Why it works**: Combines trend strength (10-day price change) with liquid confirmation (5-day average volume). Applying `ts_decay_linear` smooths the resulting weights to lower the portfolio turnover.
*   **Recommended Settings**:
    *   Neutralization: `SUBINDUSTRY`
    *   Decay: `6`

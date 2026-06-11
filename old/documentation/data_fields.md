# WorldQuant Brain Core Data Fields

The WorldQuant Brain platform provides a wide range of quantitative data fields. For standard and basic research accounts, the primary data fields consist of core pricing, transaction volume, and corporate capitalization fields.

---

## 1. Core Pricing Fields

*   `open`
    *   **Description**: The split-adjusted, dividend-adjusted market opening price of the asset on the current trading day.
    *   **Type**: Vector
    *   **Use Cases**: Analyzing intraday price ranges, open-to-open returns, and gap-ups.

*   `high`
    *   **Description**: The highest price recorded during the trading day.
    *   **Type**: Vector
    *   **Use Cases**: Volatility ranges, breakout signals, and maximum daily drawdown limits.

*   `low`
    *   **Description**: The lowest price recorded during the trading day.
    *   **Type**: Vector
    *   **Use Cases**: Calculating trading ranges and supports.

*   `close`
    *   **Description**: The split-adjusted, dividend-adjusted market closing price of the asset on the current trading day.
    *   **Type**: Vector
    *   **Use Cases**: Main pricing baseline, time-series delay calculations, and daily returns calculation.

*   `vwap`
    *   **Description**: Volume Weighted Average Price.
    *   **Type**: Vector
    *   **Math**: $\text{VWAP} = \frac{\sum (\text{Price}_i \times \text{Volume}_i)}{\sum \text{Volume}_i}$ (Calculated over intraday ticks).
    *   **Use Cases**: Ideal for institutional baseline comparisons, as it represents the true average execution price of the day and filters out opening/closing price manipulations.

*   `returns`
    *   **Description**: The daily percentage price change of the close relative to the prior close.
    *   **Type**: Vector
    *   **Math**: $\text{returns}_t = \frac{\text{close}_t - \text{close}_{t-1}}{\text{close}_{t-1}}$
    *   **Use Cases**: Baseline mean reversion inputs, short-term volatility measures, and signal momentum indicators.

---

## 2. Liquidity and Volume Fields

*   `volume`
    *   **Description**: The total number of shares traded on the market during the current trading day.
    *   **Type**: Vector
    *   **Use Cases**: Weighting alpha conviction, identifying institutional accumulation/distribution, and gating trades based on liquidity spikes.

*   `adv20`
    *   **Description**: 20-day Average Daily Volume.
    *   **Type**: Vector
    *   **Math**: $\text{adv20} = \text{ts_mean}(\text{volume}, 20)$
    *   **Use Cases**: Essential for liquidity gating (e.g. `volume > adv20`) to filter out illiquid days, or assessing stock liquidity profiles before applying heavy allocations.

---

## 3. Fundamental and Sizing Fields

*   `cap`
    *   **Description**: Market Capitalization.
    *   **Type**: Vector
    *   **Math**: $\text{Outstanding Shares} \times \text{close}$
    *   **Use Cases**: Asset sizing adjustments (e.g., scaling weights by size, or neutralizing size biases). Standard platform settings use Cap-weighted sizing.

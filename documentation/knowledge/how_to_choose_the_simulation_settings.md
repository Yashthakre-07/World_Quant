# How to Choose Simulation Settings

The exact same mathematical formula can either pass as a highly successful alpha or fail as a hard reject depending entirely on your simulation parameters. These settings define the portfolio's trading constraints and risk exposures.

---

## 1. Parameters at a Glance

When configuring a simulation, you must set five core parameters:

### A. Universe
Defines the pool of stocks your alpha trades.
*   `TOP3000`: Liquid US equities. Best for standard price, volume, and sentiment strategies.
*   `TOP1000` / `TOP500`: Concentrated large-cap stock universes. Best for capacity-rich alphas.
*   `TOP200`: Extremely liquid equities. Excellent for low-turnover fundamental alphas.

### B. Neutralization
Adjusts portfolio weights to hedge against specific systematic risks.
*   `SUBINDUSTRY`: Highly recommended! This neutralizes exposures at the tightest industry groupings. For price reversion strategies, this almost always leads to a higher Sharpe ratio by isolating pure stock-level dynamics.
*   `INDUSTRY` / `SECTOR`: Standard groupings. Best for sentiment and fundamental alphas where subindustry neutralization might remove valuable industry-wide signals.
*   `MARKET`: Broad market-hedged. Useful for macroeconomic or country-level factor alphas.

### C. Decay
Defines the smoothing factor for the alpha's weights across business days.
*   **Low Decay (0–3)**: Highly reactive. Signals update rapidly. Good for high-frequency or fast sentiment/news alphas, but yields high turnover.
*   **Medium Decay (4–8)**: Balanced. Standard for price and volume momentum alphas.
*   **High Decay (9–20)**: Slow smoothing. Vital for keeping **Turnover** low and boosting **Fitness** on fundamental value strategies that rely on quarterly reports.

### D. Delay
The latency (in days) between observation and trade execution.
*   `Delay 1`: Industry standard. If you use day $t$'s data, trades execute at the market open on day $t+1$.
*   `Delay 0`: Intraday execution. Only available on high-frequency intraday datasets, otherwise it introduces illegal look-ahead bias.

### E. Truncation
Limits the maximum weight allocation of any single stock.
*   Standard is `0.1` ($10\%$ allocation cap). Keep this at `0.1` or `0.05` to ensure adequate diversification.

---

## 2. Configuration Settings Matrix by Alpha Family

Use this matrix to set up your simulations based on the financial theme:

| Alpha Family | Target Universe | Neutralization | Ideal Decay | Delay |
| :--- | :--- | :--- | :--- | :--- |
| **Price Reversion** | `TOP3000` | `SUBINDUSTRY` | `6` to `10` | `1` |
| **Momentum** | `TOP3000` | `SUBINDUSTRY` | `8` to `12` | `1` |
| **Fundamental Value** | `TOP3000` or `TOP200` | `INDUSTRY` | `12` to `20` | `1` |
| **Social / News Sentiment** | `TOP3000` | `SUBINDUSTRY` | `4` to `8` | `1` |
| **Volume Anomalies** | `TOP3000` | `SUBINDUSTRY` | `6` to `10` | `1` |

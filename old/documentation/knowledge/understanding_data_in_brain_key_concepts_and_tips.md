# Understanding Data in BRAIN: Key Concepts and Tips

To build highly predictive alphas, you must understand the data that feeds your mathematical formulas. WorldQuant BRAIN provides access to thousands of data fields across several asset classes and markets. 

---

## 1. The Three Primary Data Categories

Datasets on the platform are categorized by their financial source:

### A. Market Data (Price & Volume)
*   **Fields**: `close`, `open`, `high`, `low`, `volume`, `vwap`.
*   **Characteristics**: Very high coverage ($99\%+$), updated daily, and highly reactive.
*   **Use Cases**: Perfect for fast short-term mean-reversion, trend-following momentum, and volatility-gated strategies.
*   **Slippage Risk**: Yields high turnover. Smooth price-based alphas with high decay to maintain high Fitness.

### B. Fundamental Data (Corporate Reports)
*   **Fields**: `enterprise_value`, `ebitda`, `pe_ratio`, `book_value`, `revenue`.
*   **Characteristics**: Updated quarterly or annually based on public company financial statements.
*   **Use Cases**: Classic value, profitability, and leverage ratios.
*   **Advantages**: Very stable values. Since reports only update every 3 months, these alphas naturally have **very low turnover**, leading to outstanding **Fitness** scores!
*   **Neutralization Tip**: Always neutralize fundamental data against `INDUSTRY` or `SUBINDUSTRY` because normal ranges for metrics like PE ratios vary wildly between sectors (e.g. Technology vs. Utilities).

### C. Alternative Data (News & Sentiment)
*   **Fields**: News sentiment scores, social media buzz, web traffic, and credit card transaction trends.
*   **Characteristics**: Noisy but highly predictive of near-term price jumps.
*   **Use Cases**: Event-driven sentiment alphas. Very powerful during high-volatility market regimes.

---

## 2. Critical Data Concepts

To ensure your backtest reflects real-world trading, keep these concepts in mind:

*   **Point-in-Time (PIT) Data**:
    *   Corporate earnings are often revised weeks after their initial release. The simulator uses **Point-in-Time** databases, meaning it only uses the exact information that was publicly available on day $t$ to simulate trades for day $t+1$. This prevents look-ahead bias.
*   **Corporate Actions Adjustments**:
    *   Prices are adjusted for stock splits, reverse splits, and cash dividends to prevent artificial price jumps/drops from registering as trading signals.
*   **Data Coverage**:
    *   Some datasets are only available for the largest 500 stocks, while others cover the entire `TOP3000`. Check the **Coverage** percentage in the Data Explorer; low-coverage fields ($<30\%$) can lead to highly concentrated weights and simulation failures.

# Clear These Tests Before Submitting an Alpha

Before your alpha can be successfully accepted for production forward-testing on WorldQuant BRAIN, it must pass a series of automated safety and compliance checks. If any of these tests fail, your submission will be rejected, regardless of how high its historical Sharpe ratio is.

---

## 1. The Core Compliance Checklist

Ensure your alpha passes the following four critical validation tests:

### A. Concentrated Weight Check (`CONCENTRATED_WEIGHT`)
*   **The Rule**: No single stock can occupy an excessively large portion of your portfolio's weights.
*   **The Risk**: High price volatility in that single stock could cause catastrophic drawdowns for the entire portfolio.
*   **How to Pass**:
    *   Do not feed raw values (like stock prices or raw volumes) directly into operators.
    *   Always normalize your signals using `rank()`, `zscore()`, or `scale()`.
    *   Ensure the `truncation` parameter in your simulation settings is set to `0.1` or `0.05`.

### B. Low Sub-Universe Sharpe Check (`LOW_SUB_UNIVERSE_SHARPE`)
*   **The Rule**: Your alpha must perform robustly when simulated on subsets of the stock universe (e.g. only large-cap stocks or only highly liquid stocks).
*   **The Risk**: An alpha that earns high returns purely by trading illiquid micro-cap stocks will fail in live trading due to execution slippage.
*   **How to Pass**:
    *   Avoid using datasets that are highly biased toward small-cap companies.
    *   Smooth your signals using liquid weighting fields like `vwap` rather than `close`.

### C. Self-Correlation Check (`SELF_CORRELATION`)
*   **The Rule**: Your new alpha must not be highly correlated with any of your previously accepted alphas.
*   **The Threshold**: The daily returns correlation (PnL vector correlation) must be strictly **$< 0.70$**.
*   **How to Pass**:
    *   Do not submit minor variations of the same formula (e.g., swapping a 5-day delta for a 6-day delta).
    *   Vary the underlying dataset family (e.g. shift from price-based to sentiment or fundamentals).

### D. Turnover Boundary Check
*   **The Rule**: Your simulated annualized turnover must be strictly between **$1.0\%$ and $70.0\%$**.
*   **How to Pass**:
    *   If turnover is too high ($>70\%$): Increase the simulation `decay` or apply a manual `ts_decay_linear()` filter.
    *   If turnover is too low ($<1\%$): The alpha is trading too slowly to react to new signals. Shorten your time-series window lengths (e.g. from 20 days to 10 days) or reduce `decay`.

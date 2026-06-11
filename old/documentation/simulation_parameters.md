# Simulation Parameters Guide

When submitting an alpha to the WorldQuant Brain simulation endpoint (`/api/v1/simulations`), you must define the operational and risk constraints under which the alpha runs. These constraints dictate the universe of stocks, processing delays, and portfolio sizing.

---

## 1. Parameters Reference

*   `universe`
    *   **Description**: The portfolio of assets tested. For basic and competitive accounts, the standard target universe is `TOP3000`.
    *   **Options**: `TOP3000` (liquid US equities), `TOP2000`, `TOP1000`.
    *   **Impact**: Limits your alpha's universe. A liquid universe helps lower market impact costs and execution slippage.

*   `region`
    *   **Description**: The geographic jurisdiction of the assets.
    *   **Standard**: `USA` (for US domestic market research).
    *   **Options**: `USA`, `EUR`, `ASI`.

*   `decay`
    *   **Description**: The portfolio weight decay horizon. It acts as an exponential/linear weight-smoothing parameter.
    *   **Standard**: `6` to `10`.
    *   **Impact**: Higher decay (e.g. `12` or `15`) dramatically reduces portfolio **Turnover** (since daily position size adjustments are smoothed over multiple days). However, it adds a lag to signal updates, which can occasionally lower the Sharpe ratio.

*   `neutralization`
    *   **Description**: The portfolio sector risk hedging constraint.
    *   **Options**:
        *   `SECTOR`: Neutralizes at the broad sector level (e.g., Finance, Tech).
        *   `INDUSTRY`: Neutralizes at the industry level (e.g., Software, Hardware).
        *   `SUBINDUSTRY`: Neutralizes at the tightest subindustry level (e.g., Application Software). **Highly recommended for standard reversion alphas because it yields higher Sharpe Ratios.**
        *   `MARKET`: Neutralizes broad market beta only.

*   `delay`
    *   **Description**: The execution latency (in days) between observation and execution.
    *   **Standard**: `1`.
    *   **Impact**: Delay 1 means a signal calculated using day $t$'s market data executes at the market open on day $t+1$. Delay 0 is typically forbidden on standard datasets as it introduces look-ahead bias (using price info to trade on the same day).

*   `truncation`
    *   **Description**: The maximum leverage or allocation limit for any single stock.
    *   **Standard**: `0.1` (10% allocation limit).
    *   **Impact**: Prevents your portfolio from taking overly concentrated bets on single stocks, diversifying the alpha.

*   `pasteurization`
    *   **Description**: Controls whether outlier weight values are automatically winsorized.
    *   **Standard**: `ON`.

*   `unitHandling`
    *   **Description**: Ensures dimensional consistency checks.
    *   **Standard**: `VERIFY`.

---

## 2. Standard Simulation Settings Payload Example

```json
{
  "nanHandling": "OFF",
  "instrumentType": "EQUITY",
  "delay": 1,
  "universe": "TOP3000",
  "truncation": 0.1,
  "unitHandling": "VERIFY",
  "pasteurization": "ON",
  "region": "USA",
  "language": "FASTEXPR",
  "decay": 8,
  "neutralization": "SUBINDUSTRY",
  "visualization": false
}
```

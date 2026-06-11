# Simulate Your First Alpha

Simulating an alpha is the core action on WorldQuant BRAIN. Whether you are using the web interface or writing an automated script using the WorldQuant Brain API, this guide explains how to properly construct and submit a simulation job.

---

## 1. Constructing the Simulation Payload

To run a backtest, you must combine your mathematical formula with a set of operational parameters. Here is the standard JSON structure used to submit simulations via the `/api/v1/simulations` API:

```json
{
  "formula": "rank(vwap - close) / rank(volume)",
  "settings": {
    "nanHandling": "OFF",
    "instrumentType": "EQUITY",
    "delay": 1,
    "universe": "TOP3000",
    "truncation": 0.1,
    "unitHandling": "VERIFY",
    "pasteurization": "ON",
    "region": "USA",
    "language": "FASTEXPR",
    "decay": 6,
    "neutralization": "SUBINDUSTRY"
  }
}
```

### Critical Payload Keys:
*   `formula`: The FastExpression text representing your signal.
*   `universe`: The stock pool (typically `TOP3000`).
*   `neutralization`: The risk-adjustment level (typically `SUBINDUSTRY`).
*   `decay`: The portfolio smoothing window (typically `6` or `8`).

---

## 2. Running Simulations in the Web UI

If you are using the BRAIN web portal:
1.  **Open the Simulator**: Navigate to the **Simulator** page.
2.  **Paste Your Expression**: Enter your FASTEXPR formula in the large expression text box.
3.  **Configure Settings**: In the settings side-bar, set the Region, Universe, Neutralization, Decay, and Truncation according to your hypothesis.
4.  **Click Simulate**: Click the **Simulate** button. The interface will transition to a loading state.

---

## 3. The Life-Cycle of a Simulation Job

When a simulation is submitted, it goes through several states:
1.  **QUEUED**: The job is waiting for an available worker thread on WorldQuant's cluster.
2.  **RUNNING**: The engine is running your formula on historical data (usually covering $20+$ years).
3.  **COMPLETED**: The backtest is complete, and the performance report (Sharpe, Turnover, Fitness) is generated.
4.  **ERROR**: The simulation failed due to a syntax error or a weight concentration check.

---

## 4. Troubleshooting Initial Failures

If your first simulation returns an `ERROR` or `HARD_REJECT`, check the following:
*   **Is the syntax correct?** FastExpression is case-sensitive. Check if you wrote `ts_mean` instead of `TS_MEAN`.
*   **Are parentheses balanced?** Each opening parenthesis `(` must have a matching closing parenthesis `)`.
*   **Did it fail weight checks?** If you receive a weight concentration error, wrap your raw signals in `rank()` or `zscore()` to prevent a few extreme stocks from dominating the portfolio weights.

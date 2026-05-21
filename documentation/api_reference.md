# WorldQuant Brain REST API Reference

The WorldQuant Brain REST API provides an automated interface to authenticate sessions, submit simulation payloads, poll job progress, retrieve performance details, and submit passing alphas for production tracking.

---

## 1. Authentication Flow
Authentication uses standard HTTP Basic Auth via your platform email and password to retrieve a persistent cookie-based session.

*   **Endpoint**: `POST https://api.worldquantbrain.com/sessions`
*   **Request Headers**:
    *   `Authorization: Basic <base64(email:password)>`
*   **Response**:
    *   Sets session cookies (e.g., `brain_session`). These cookies must be included in all subsequent requests.

---

## 2. Simulation Submission
Submits a FASTEXPR formula to be compiled and backtested on WorldQuant's high-performance cluster.

*   **Endpoint**: `POST https://api.worldquantbrain.com/simulations`
*   **Content-Type**: `application/json`
*   **Payload Format**:
    ```json
    {
      "regular": "group_neutralize(-rank(ts_decay_linear(close - open, 2)), subindustry)",
      "type": "REGULAR",
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
        "decay": 8,
        "neutralization": "SUBINDUSTRY",
        "visualization": false
      }
    }
    ```
*   **Response Headers**:
    *   `Location`: Polling endpoint URL (e.g. `https://api.worldquantbrain.com/simulations/XYZ123`).

---

## 3. Simulation Job Polling
Retrieves the compilation status of the simulation.

*   **Endpoint**: `GET https://api.worldquantbrain.com/simulations/<simulation_id>`
*   **Response Payload Fields**:
    *   `progress`: Floating-point value from `0.0` to `1.0` indicating backtest completion.
    *   `alpha`: Present once backtesting is complete. Holds the uniquely generated **Alpha ID** (e.g., `mLqGAvRX`).
    *   `message`: Contains compilation error warnings if the FASTEXPR syntax check fails.

---

## 4. Alpha Performance Retrieval
Retrieves the mathematical performance metrics of a successfully backtested alpha.

*   **Endpoint**: `GET https://api.worldquantbrain.com/alphas/<alpha_id>`
*   **Response Payload Structure**:
    *   `is`: Performance metrics on the In-Sample dataset.
        *   `sharpe`: In-sample Sharpe ratio.
        *   `fitness`: In-sample Fitness ratio.
        *   `turnover`: Annualized turnover value (multiply by 100 to get percentage).
        *   `checks`: Array of compliance validation results.
            *   `name`: e.g. `CONCENTRATED_WEIGHT`.
            *   `result`: `PASS` or `FAIL`.

---

## 5. Production Submission
Triggers the formal submission of a qualified alpha.

*   **Step 1: Initiate Check**
    *   **Endpoint**: `POST https://api.worldquantbrain.com/alphas/<alpha_id>/submit`
    *   **Description**: Begins the automated multi-universe correlation check.
*   **Step 2: Await Submission Approval**
    *   **Endpoint**: `GET https://api.worldquantbrain.com/alphas/<alpha_id>/submit`
    *   **Description**: Polls check progress.
    *   **Completion Criteria**: Endpoint returns `HTTP 404` when the alpha has completed checks and successfully registered on the user's production tracking board.

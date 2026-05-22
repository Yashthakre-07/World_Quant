# WorldQuant Brain Research Pipeline: Exhaustive Operations & Blueprint Manifest

This manifest is the single source of truth for the **AlphaForge Automation Pipeline**. It defines the entire technical architecture, environment variables, SQLite database schemas, quantitative performance thresholds, failure diagnostics, and magic operational code words.

---

## 🔴 0. CRITICAL PROTOCOLS FOR FUTURE AI AGENTS (MANDATORY)

Every future AI agent or developer loading this workspace **MUST STRICTLY FOLLOW** these absolute rules:

1. **READ MANDATORY GUIDES FIRST**: You must read `instructions.md` and `research.md` in full before running any code, submitting alphas, or suggesting formulas. Do not attempt to guess or hallucinate.
2. **STRICT CONCURRENCY LOCK (3 ACTIVE MAX)**: Never modify `MAX_CONCURRENT_SIMS` to be higher than `3` in `src/config.py`. Exceeding 3 parallel simulations on the WorldQuant cluster will result in immediate API rate limits and cluster blocks.
3. **MANDATORY 20-SECOND SPACING**: All POST requests to the `/simulations` endpoint must be thread-locked and spaced sequentially by a minimum of **20 seconds**. Never dump concurrent requests onto the platform.
4. **LOCAL SYNTAX SANITY CHECK**: You must pass every proposed formula through `src/validator.py` locally before requesting network backtests. Any formula with unbalanced brackets, Python keywords (`and`/`or`), or premium variables must be rejected immediately without hitting the network.
5. **GATED SIGNAL SYNTHESIS ONLY**: You are strictly prohibited from submitting raw, un-smoothed price signals. All custom alpha formulas must be constructed using the **Gated Reversion Blueprint** detailed in [research.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/research.md):
   $$\text{Alpha} = \text{Neutralize} \left( \text{TradeWhen} \left( \text{volume} > \text{adv20} \times K, \text{-rank} \left( \text{ts\_decay\_linear} \left( \text{SIGNAL}, N \right) \right), 0 \right), \text{subindustry} \right)$$
   Where $K \in [0.5, 0.8]$ and $N \in [3, 5]$.
6. **LIVING RESEARCH DOCUMENTATION**: Whenever a backtest completes, query `db/alpha_vault.db`. If you identify a formula that successfully qualifies for submission (Sharpe $\ge 1.25$, Fitness $\ge 1.0$), you must immediately write the formula, parameters, and structural insights into the research file [research.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/research.md). Keep this manual continuously updated with fresh, successful quant ideas.
7. **RED COLOR TAGGING**: Any qualified alpha must be patched with the color **"RED"** on the remote server via the `/alphas/{id}` API endpoint immediately upon submission.

---

## 🔑 1. Quickstart Commands (The Magic Code Words)

To run the quant workflow with zero friction, execute these commands or type the exact phrase in our chat:

| Chat Code Word | Core Action | Underlying Script | Description |
| :--- | :--- | :--- | :--- |
| **`LOGIN`** | Authenticates session | `python check_simulations.py` | Reloads `WQSession` cookies, contacts `/users/self` to check token validity, decodes the JWT to find the exact epoch expiry, and displays telemetry. |
| **`START PIPELINE`** | Runs queue | `python run_pipeline.py` | Launches the Flask telemetry dashboard on port 8000 and executes the queue under a strict 3-worker limit. |
| **`PUSH CODES`** | Appends new alphas | `python manage_queue.py append` | Appends up to 5 unique, compliant price/volume formulas from pool to `db/simulation_queue.json`. |
| **`LOAD CODES`** | Replaces old queue | `python manage_queue.py replace` | Overwrites `db/simulation_queue.json` completely with a fresh set of 5 pricing/volume-based formulas. |

---

## ⚙️ 2. Core Platform Configurations & Rules

### A. Strict Concurrency Cap (`MAX_CONCURRENT_SIMS = 3`)
* **Context**: The WorldQuant Brain platform restricts standard/basic research accounts to exactly **3 concurrent active simulations** on the server cluster.
* **Orchestration**: `run_pipeline.py` initiates a `ThreadPoolExecutor(max_workers=3)`.
* **Dashboard Mapping**: The first 3 alphas in the queue are processed in parallel (`SIMULATING`), while subsequent alphas are initialized as `PENDING` (progress `0%`). As soon as an active thread completes (status becomes `SUBMITTED`, `SOFT_FAIL`, or `ERROR`), the executor immediately schedules the next pending alpha.

### B. 20-Second Submission Lock Spacing
* **Context**: Sending concurrent API requests to the WorldQuant `/simulations` endpoint at the exact same second triggers platform security blockages and IP rate locks.
* **Orchestration**: A global `submission_lock = threading.Lock()` is acquired inside `simulate_task`. Before sending the POST request, the thread sleeps for exactly **20 seconds** within the lock. This forces a clean, sequential, rate-limit-compliant spacing.

### C. Standard Pricing & Liquidity Fields Only
* **Context**: Standard research accounts do *not* have subscription rights to premium datasets (e.g., EBITDA, Analyst consensus, News Sentiment vectors). Using them results in immediate access or syntax errors.
* **Allowed Fields**:
  * `open`, `high`, `low`, `close` (Pricing variables)
  * `vwap` (Volume Weighted Average Price)
  * `volume` (Intraday volume)
  * `returns` (Close-to-close returns)
  * `adv20` (20-day Average Daily Volume)
  * `cap` (Market Capitalization)

### D. Dynamic Queue Scheduling Engine
* **Context**: Traditional backtesters require hard restarts to add new alphas, terminating active threads.
* **Orchestration**: The pipeline utilizes an infinite `while True` loop that polls `db/simulation_queue.json` every 3 seconds. When you push new alphas (via `append`), the scheduler dynamically submits them to the active `ThreadPoolExecutor` via `.submit()`. The new alphas are seamlessly queued below active tasks as `PENDING` without affecting currently running simulations.

### E. Dynamic Rate-Limit Jitter and Retry Mechanics
* **Context**: Frequent standard tier requests can trigger `HTTP 429` (Too Many Requests).
* **Orchestration**: The worker thread automatically catches `HTTP 429` responses, sets the alpha state back to `PENDING` (0% progress), calculates a randomized sleep buffer (e.g. `30 to 45 seconds` of dynamic jitter), waits, and recursively re-executes the submission. This shields the research profile from systemic lockouts.

---

## 🛡️ 3. Built-In Pre-Submission Local Validator

To prevent socket hangs, thundering-herd blocks, or remote cluster compile errors, the pipeline runs a local validation pass via `src/validator.py` before making any API requests.

### Validation Diagnostics
1. **Bracket Matching**: Recursively checks bracket nesting (`()`, `[]`, `{}`) for unbalanced openings or mismatched pairs.
2. **Token Security**: Checks every word against a white-list of `ALLOWED_FIELDS` and `ALLOWED_OPS`. If a variable like `anl4_ebitda` or a custom operator is present, it is rejected instantly.
3. **Python Leaks**: Rejects Python comparisons (`and`, `or`, `not`) and enforces standard platform operators (`&&`, `||`, `!`).
4. **Behavior**: If validation fails, the alpha's status is set directly to `ERROR` on the dashboard, the vault record is updated, and the remote API call is bypassed entirely.

---

## 🗄️ 4. SQLite Database Schema (`db/alpha_vault.db`)

All backtest metrics, simulation properties, and API results are stored in the SQLite database to track historical progress.

### A. Table: `alpha_runs`
Stores every individual simulation attempt.
```sql
CREATE TABLE IF NOT EXISTS alpha_runs (
    run_id TEXT PRIMARY KEY,          -- Unique run ID (UUID prefix)
    family TEXT,                      -- e.g., "Price Reversion", "Volume Anomaly"
    hypothesis TEXT,                  -- The economic rationale
    formula TEXT,                     -- The actual math factor
    region TEXT DEFAULT 'USA',        -- e.g., "USA"
    universe TEXT DEFAULT 'TOP3000',  -- e.g., "TOP3000"
    neutralization TEXT,              -- e.g., "SUBINDUSTRY"
    decay INTEGER,                    -- decay parameter
    truncation REAL,                  -- e.g., 0.08 or 0.10
    delay INTEGER,                    -- e.g., 1 or 2
    sharpe REAL,                      -- Sharpe Ratio metric
    fitness REAL,                     -- Fitness metric
    turnover REAL,                    -- Turnover metric (%)
    checks_passed INTEGER,            -- Number of platform checks passed
    weight_check TEXT,                -- "PASS" or "FAIL" (weight concentration)
    sub_sharpe REAL,                  -- Sub-universe Sharpe Ratio
    status TEXT,                      -- "SUBMITTED", "SOFT_FAIL", "ERROR", "HARD_REJECT"
    alpha_link TEXT,                  -- platform alpha URL
    sim_link TEXT,                    -- platform simulation progress URL
    error_message TEXT,               -- Detailed failure logs if any
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### B. Table: `submitted_alphas`
Stores alphas that successfully satisfy the platform's production guidelines.
```sql
CREATE TABLE IF NOT EXISTS submitted_alphas (
    alpha_id TEXT PRIMARY KEY,        -- WorldQuant Alpha ID
    formula TEXT,                     -- The math factor
    sharpe REAL,                      -- Sharpe Ratio metric
    fitness REAL,                     -- Fitness metric
    turnover REAL,                    -- Turnover metric (%)
    color TEXT DEFAULT 'RED',         -- Color tag on platform
    correlation_checked INTEGER,      -- 1 if checked, 0 otherwise
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📊 5. Production Qualification Guidelines

To transition an alpha from a backtest to **Submitted** state, the platform evaluates it against these strict mathematical thresholds:

* **Sharpe Ratio**: $\ge 1.25$ (In-sample stability)
* **Fitness Metric**: $\ge 1.0$ (Risk-adjusted payout ratio: $\text{Sharpe} \times \sqrt{|\text{Returns}|/\text{Turnover}}$)
* **Turnover**: $1.0\% \le \text{Turnover} \le 70.0\%$
* **Sub-universe Sharpe**: $\ge 0.5$ (Out-of-sample robustness check on smaller subsets)
* **Weight Concentration**: Max weight per instrument must satisfy diversification rules.
* **Neutralization**: Sector or Subindustry peers (Subindustry is optimal for price/volume mean reversion).
* **Tagging Requirement**: Qualifying factors must be patched with `{"color": "RED"}` on the remote server for tracking.

---

## 🔍 6. Session Management & JWT Token Decoding

The authentication system is managed dynamically by `src/auth.py`. 
* **Persisted Credentials**: Loaded from `sai.env` containing the `WQ_EMAIL` and `WQ_PASSWORD` variables.
* **Token Caching**: Persisted to `db/session_cookies_saineela731_gmail_com.json`.
* **JWT Decoding Logic**:
  To obtain the session expiration without making API calls, `run_pipeline.py` decodes the token dynamically:
  ```python
  token = cookies.get("t", "")
  payload_b64 = token.split(".")[1]
  padding = 4 - len(payload_b64) % 4
  payload_b64 += "=" * padding
  payload = json.loads(base64.urlsafe_b64decode(payload_b64))
  exp_epoch = payload.get("exp", 0)
  ```
  The countdown is rendered dynamically at the top right of the dashboard.

---

## 🧬 7. Compliant Queue Blueprint & Alpha Catalog (`db/simulation_queue.json`)

The primary simulation queue contains 15 elite, 100% compliant pricing/volume alphas designed under our strict **Gated Reversion Blueprint** to contain turnover and bypass correlation checks:

```json
[
  {
    "family": "Price Reversion",
    "hypothesis": "Intraday close-to-open gaps represent temporary imbalances that revert; 3-day decay smoothing limits turnover.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear(close - open, 3)), 0), subindustry)"
  },
  {
    "family": "VWAP-Price Divergence",
    "hypothesis": "Deviations between the closing price and vwap volume centers represent unstable intraday drifts that revert.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear((close - vwap) / (ts_std_dev(close, 20) + 0.001), 3)), 0), subindustry)"
  },
  {
    "family": "Price Reversion",
    "hypothesis": "Short-term returns mean-revert on highly liquid sessions when institutional trade volumes are elevated.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.5, -rank(ts_decay_linear(returns, 3)), 0), subindustry)"
  },
  {
    "family": "Overnight Gap Reversion",
    "hypothesis": "Opening price gaps relative to the previous close represent liquidity mismatches that mean-revert intraday.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear(open - ts_delay(close, 1), 3)), 0), subindustry)"
  },
  {
    "family": "Spread Reversion",
    "hypothesis": "Peaks in the intraday high-low spread indicate temporary volatility spikes that mean-revert on typical trading days.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(high - low, 3)), 0), subindustry)"
  },
  {
    "family": "VWAP Trend Reversion",
    "hypothesis": "Intraday drift between the volume center (vwap) and open price represents overextended liquidity that reverts.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(vwap - open, 3)), 0), subindustry)"
  },
  {
    "family": "Volume-Weighted Return Reversion",
    "hypothesis": "Returns weighted by volume deviations capture amplified trade imbalances that experience sharp reversion.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.55, -rank(ts_decay_linear(returns * rank(volume / adv20), 3)), 0), subindustry)"
  },
  {
    "family": "Overnight Trend Reversion",
    "hypothesis": "Extended 2-day gapped intraday movements represent overbought/oversold momentum exhaustion that mean-reverts.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.8, -rank(ts_decay_linear(open - ts_delay(close, 2), 3)), 0), subindustry)"
  },
  {
    "family": "Normalized Deviation Reversion",
    "hypothesis": "Normalized closing price deviation from the 10-day moving average mean-reverts on active trading sessions.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear((close - ts_mean(close, 10)) / (ts_std_dev(close, 10) + 0.001), 3)), 0), subindustry)"
  },
  {
    "family": "Intraday Volatility Reversion",
    "hypothesis": "Intraday high price deviation relative to the volume center represents temporary buying exhaustion that mean-reverts.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(high - vwap, 3)), 0), subindustry)"
  },
  {
    "family": "Volatility Ratio Reversion",
    "hypothesis": "Intraday standardized high-low ranges represent excessive volatility peaks that mean-revert on highly liquid sessions.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear((high - low) / (ts_std_dev(close, 20) + 0.001), 3)), 0), subindustry)"
  },
  {
    "family": "Price-VWAP Divergence Ratio",
    "hypothesis": "The ratio of closing price to volume average price indicates temporary deviations that revert in active market sessions.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(close / (vwap + 0.001) - 1, 3)), 0), subindustry)"
  },
  {
    "family": "Standardized Intraday Reversion",
    "hypothesis": "Extreme differences between close and open prices standardized by dynamic standard deviations revert on liquid days.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear((close - open) / (ts_std_dev(returns, 10) + 0.0001), 3)), 0), subindustry)"
  },
  {
    "family": "Multi-Day Price Reversion",
    "hypothesis": "Medium-term 2-day delayed price changes represent overextended trends that mean-revert on liquid trading sessions.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(close - ts_delay(close, 2), 3)), 0), subindustry)"
  },
  {
    "family": "Intraday Bottom Reversion",
    "hypothesis": "Low price deviations relative to the volume center average represent extreme selling pressure peaks that mean-revert.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, rank(ts_decay_linear(vwap - low, 3)), 0), subindustry)"
  }
]
```

---

## 🔬 8. Quantitative Synthesis & Research Manual

For deep mathematical deconstructions of successful historical formulas, parameter sweet-spot boundaries, and custom signal synthesis templates, consult the [Quantitative Research Manual (research.md)](file:///c:/Users/Admin/Documents/VIBE_YT/wq/research.md).

---

## 🌐 9. Cloud Infrastructure & Deployment Specs (Render)

The quantitative research pipeline is optimized to run autonomously 24/7 in the cloud using **Render** web hosting.

### A. Process-Safe Dynamic State Synchronizer
To support multi-process WSGI / Gunicorn environments where memory space is isolated:
* The Flask dashboard `/api/status` dynamically queries the SQLite database (`db/alpha_vault.db`) and disk-based simulation queue (`db/simulation_queue.json`) on every call.
* This guarantees 100% accurate, synced status readouts regardless of which concurrent worker process serves the HTTP request.

### B. Persistent Disk Storage
* Render uses a persistent volume (`/data` or `db/`) to preserve SQLite databases and user session cookies (`db/session_cookies_*.json`) between container restarts, ensuring biometric persona logins remain valid.

---

## 📡 10. Secure API Bridge Specification

The cloud instance exposes a full suite of secure API routes that let you remotely manage the simulation queue **without restarting or redeploying** the pipeline. All write operations require the Bearer token.

* **Live Render URL**: `https://world-quant.onrender.com`
* **Authorization Header**: `Authorization: Bearer yashthakreop` (set via `API_SECRET_TOKEN` environment variable on Render)

### A. Push New Alphas (Append)
* **HTTP Route**: `POST /api/queue-alpha`
* **Behavior**: Appends new alphas to the end of the queue. Automatically deduplicates — if a formula already exists in the queue or in-memory pipeline, it is skipped.
* **Payload Structure**:
  ```json
  [
    {
      "family": "Price Range Position Reversal",
      "hypothesis": "Williams-style range percentile reversal...",
      "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear((close - low) / (high - low + 0.001), 5)), 0), subindustry)",
      "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
    }
  ]
  ```
* **PowerShell Example**:
  ```powershell
  $headers = @{ "Authorization" = "Bearer yashthakreop"; "Content-Type" = "application/json" }
  $body = '[{"family":"My Alpha","hypothesis":"...","formula":"...","settings":{...}}]'
  Invoke-RestMethod -Uri "https://world-quant.onrender.com/api/queue-alpha" -Method POST -Headers $headers -Body $body
  ```

### B. Overwrite Queue (Replace All)
* **HTTP Route**: `POST /api/overwrite-queue`
* **Behavior**: Completely wipes the existing queue on disk and replaces it with the provided alphas. Use when you want a fresh start without clearing + appending separately.
* **Payload**: Same JSON array format as `/api/queue-alpha`.

### C. Clear Queue (Empty)
* **HTTP Route**: `POST /api/clear-queue`
* **Behavior**: Empties the entire on-disk queue (`db/simulation_queue.json`). Currently running simulations are NOT affected — they will finish naturally.
* **Payload**: None required (empty body is fine).

### D. Queue Status (Read-Only)
* **HTTP Route**: `GET /api/queue-status`
* **Authorization**: None required (public read endpoint).
* **Returns**: Number of queued alphas on disk and in memory, pipeline status, and truncated formula previews.

---

## 🚨 11. Critical Syntax Rules & Gotchas

### A. Element-wise vs Time-Series `max`/`min`
This is the **#1 most common syntax error** that causes cluster compile failures:
| Intent | ❌ WRONG | ✅ CORRECT |
|---|---|---|
| Max of two fields at same timestamp | `ts_max(open, close)` | `max(open, close)` |
| Min of two fields at same timestamp | `ts_min(open, close)` | `min(open, close)` |
| Highest value over N rolling days | `max(close, 10)` | `ts_max(close, 10)` |
| Lowest value over N rolling days | `min(low, 10)` | `ts_min(low, 10)` |

**Rule**: `ts_max(x, d)` and `ts_min(x, d)` require a **day count** `d` as the second argument. For comparing two fields element-wise, use bare `max(x, y)` and `min(x, y)`.

### B. RED Color Tagging Policy
* **Only alphas with status `SUBMITTED`** (fully passed all production board checks including self-correlation) should be tagged RED via the `/alphas/{id}` PATCH endpoint.
* `SOFT_FAIL`, `HARD_REJECT`, and `ERROR` alphas must **NEVER** be tagged RED.
* This policy is enforced in `run_pipeline.py` line ~1472.

### C. Division-by-Zero Guards
* Always add a small epsilon (`+ 0.001` or `+ 0.0001`) when dividing by fields that can be zero (e.g., `high - low`, `ts_std_dev(...)`).

---

## ⚡ 12. Self-Ping Keep-Alive Heartbeat

* To prevent Render free tier servers from spinning down after 15 minutes of inactivity:
* A background thread `self_ping_loop()` starts alongside Flask.
* Every **60 seconds**, the script sends an HTTP GET request to its own `/api/queue-status` endpoint.
* This creates a continuous stream of incoming traffic, ensuring the cloud container runs at peak performance indefinitely!


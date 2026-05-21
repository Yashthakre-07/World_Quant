# WorldQuant Brain Alpha Agent — Production Project Plan
## Codename: AlphaForge

> This plan is built from reverse-engineering the **actual working API** (from WQ-Brain, Brainiac repos), real submission criteria from top 1.3% competitors, and the proven 101 Formulaic Alphas paper.

---

## 1. CONFIRMED API ARCHITECTURE (Real Endpoints)

All endpoints verified from the WQ-Brain open-source project (220+ stars, 68 forks).

### 1.1 Authentication
```
POST https://api.worldquantbrain.com/authentication
```
- Uses HTTP Basic Auth: `session.auth = (email, password)`
- Returns a session cookie (NOT a Bearer token — the `requests.Session` object holds it automatically)
- May trigger **biometric/Persona verification** — response contains `inquiry` field
- Biometric URL: `{response.url}/persona?inquiry={inquiry_id}`
- Session persists via cookies, no manual JWT management needed

### 1.2 Simulation
```
POST https://api.worldquantbrain.com/simulations
```
**Exact JSON payload (confirmed working):**
```json
{
  "regular": "<alpha_expression>",
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
    "decay": 6,
    "neutralization": "SUBINDUSTRY",
    "visualization": false
  }
}
```
- Returns `Location` header with simulation polling URL
- Poll that URL with GET until `response.json()` contains `"alpha"` key
- Progress available via `response.json()["progress"]` (0.0 to 1.0)
- Poll interval: **10 seconds**
- Typical completion: **30–120 seconds**

### 1.3 Alpha Results
```
GET https://api.worldquantbrain.com/alphas/{alpha_id}
```
Returns full IS (In-Sample) metrics:
- `r["is"]["sharpe"]` — Sharpe ratio
- `r["is"]["fitness"]` — Fitness score
- `r["is"]["turnover"]` — Turnover (decimal, multiply by 100 for %)
- `r["is"]["checks"]` — Array of pass/fail checks including:
  - `CONCENTRATED_WEIGHT` — weight distribution check
  - `LOW_SUB_UNIVERSE_SHARPE` — sub-universe performance

### 1.4 Alpha Submission
```
POST https://api.worldquantbrain.com/alphas/{alpha_id}/submit
GET  https://api.worldquantbrain.com/alphas/{alpha_id}/submit  (poll for result)
```
- POST triggers submission
- GET polls until `response.content` is non-empty
- Checks include `SELF_CORRELATION` — compares against your existing submitted alphas
- 404 = alpha already submitted

---

## 2. OPERATOR & DATA VOCABULARY (Complete Reference)

### 2.1 Price Fields
`open`, `high`, `low`, `close`, `vwap`, `returns`

### 2.2 Volume/Market Fields
`volume`, `adv20` (20-day average daily volume), `cap` (market capitalization)

### 2.3 Cross-Sectional Operators
| Operator | Description |
|:---|:---|
| `rank(x)` | Rank across universe (0 to 1) |
| `zscore(x)` | Z-score across universe |
| `sigmoid(x)` | Sigmoid transform |
| `scale(x)` | Scale to sum=0 |
| `log(x)`, `exp(x)` | Log/Exp transforms |
| `fraction(x)` | Fractional rank |
| `sign(x)`, `abs(x)` | Sign/Absolute |
| `signed_power(x, p)` | Preserves sign in power |
| `pasteurize(x)` | Removes outlier artifacts |

### 2.4 Time-Series Operators
| Operator | Description |
|:---|:---|
| `ts_delta(x, d)` | `x - ts_delay(x, d)` |
| `ts_delay(x, d)` | Value d days ago |
| `ts_rank(x, d)` | Rank of current vs last d values |
| `ts_sum(x, d)` | Rolling sum |
| `ts_mean(x, d)` | Rolling mean (use `ts_sum(x,d)/d`) |
| `ts_std_dev(x, d)` | Rolling std deviation |
| `ts_corr(x, y, d)` | Rolling correlation |
| `ts_covariance(x, y, d)` | Rolling covariance |
| `ts_regression(x, y, d)` | Rolling regression |
| `ts_decay_linear(x, d)` | Linear decay weighting |
| `ts_product(x, d)` | Rolling product |
| `ts_max(x, d)`, `ts_min(x, d)` | Rolling max/min |
| `ts_arg_max(x, d)`, `ts_arg_min(x, d)` | Index of max/min |
| `ts_max_diff(x, d)`, `ts_min_diff(x, d)` | Diff from max/min |
| `ts_av_diff(x, d)` | Average difference |
| `ts_ir(x, d)` | Information ratio |
| `ts_skewness(x, d)`, `ts_kurtosis(x, d)` | Higher moments |
| `ts_entropy(x, d)` | Entropy measure |
| `ts_median(x, d)` | Rolling median |

### 2.5 Group Operators
| Operator | Description |
|:---|:---|
| `group_neutralize(x, group)` | Neutralize within group |
| `group_zscore(x, group)` | Z-score within group |
| `group_rank(x, group)` | Rank within group |
| `group_mean(x, n, group)` | Mean within group |
| `group_std_dev(x, group)` | Std dev within group |
| `group_sum(x, group)` | Sum within group |
| `group_scale(x, group)` | Scale within group |
| `group_max(x, group)` | Max within group |
| `group_median(x, group)` | Median within group |

**Group types:** `market`, `sector`, `industry`, `subindustry`

### 2.6 Conditional/Special
- Ternary: `condition ? value_if_true : value_if_false`
- Logical: `&&` (AND), `||` (OR)
- Comparison: `>`, `<`, `==`
- `trade_when(entry_cond, alpha_expr, exit_val)` — Controls when to trade

---

## 3. SUBMISSION QUALITY GATES (Real Thresholds)

From WQ-Brain IS Pass Criterion and top competitor data:

### 3.1 Hard Requirements (Must Pass ALL)
| Check | Threshold |
|:---|:---|
| Sharpe Ratio | > 1.25 |
| Fitness | >= 1.0 |
| Turnover | > 1% AND < 70% |
| Weight Distribution | Not concentrated (no single stock > ~10%) |
| Sub-Universe Sharpe | Must pass (varies by region) |

### 3.2 Self-Correlation Gate (Submission Only)
- Compares new alpha PnL against ALL your previously submitted alphas over 2-year window
- **Exception**: If new alpha's Sharpe is >= 10% higher than the correlated alpha, it can still pass

### 3.3 Our Agent's Internal Tiers
| Tier | Sharpe | Fitness | Turnover | Action |
|:---|:---|:---|:---|:---|
| **HARD_REJECT** | < 1.0 | < 0.8 | < 1% or > 70% | Discard, log failure reason |
| **SOFT_FAIL** | 1.0–1.25 | 0.8–1.0 | Borderline | Retry with different settings |
| **SUBMITTABLE** | > 1.25 | >= 1.0 | 1–70% | Submit to Brain |
| **EXCELLENT** | > 1.5 | > 1.3 | 5–50% | Submit + flag as template for future |

---

## 4. THE 6 ALPHA FAMILIES (Proven Working Formulas)

Each family has **seed expressions** sourced from the 101 Formulaic Alphas paper and WQ-Brain's working commands. The LLM generates variations of these, never random.

### Family 1: Price Reversion
**Hypothesis**: Stocks that deviate from their average revert.
```
Seed: (high + low)/2 - close
Seed: rank(close - ts_mean(close, 5))
Seed: -rank(ts_delta(close, 5))
Seed: scale(((ts_sum(close, 7) / 7) - close)) + (20 * scale(ts_corr(vwap, ts_delay(close, 5), 230)))
```
**Settings**: Universe=TOP3000, Neutralization=MARKET, Decay=6–10

### Family 2: Volatility-Gated Reversion
**Hypothesis**: Trade reversion only during high-volatility regimes.
```
Seed: trade_when(ts_rank(ts_std_dev(returns, 22), 252) > 0.55, -ts_regression(returns, ts_lag(returns,1), 252), -1)
Seed: (-1 * rank(ts_std_dev(high, 10))) * ts_corr(high, volume, 10)
```
**Settings**: Universe=TOP3000, Neutralization=SUBINDUSTRY, Decay=10–15

### Family 3: Fundamental Value
**Hypothesis**: Cheap stocks (low EV/EBITDA, high earnings yield) outperform.
```
Seed: -ts_zscore(enterprise_value/ebitda, 63)
Seed: rank((1 / close)) * volume / ts_mean(volume, 20)
Seed: 0 - (1 * (rank((ts_sum(returns, 10) / ts_sum(ts_sum(returns, 2), 3))) * rank((returns * cap))))
```
**Settings**: Universe=TOP1000, Neutralization=INDUSTRY, Decay=15–20, Truncation=0.05

### Family 4: Volume Anomaly
**Hypothesis**: Unusual volume patterns predict price direction.
```
Seed: group_neutralize(volume/(ts_sum(volume,60)/60), sector)
Seed: ts_rank((volume / ts_mean(volume,20)), 20) * ts_rank((-1 * ts_delta(close, 7)), 8)
Seed: (sign(ts_delta(volume, 1)) * (-1 * ts_delta(close, 1)))
Seed: log(pasteurize(vwap/close))
```
**Settings**: Universe=TOP3000, Neutralization=SUBINDUSTRY, Decay=6

### Family 5: Cross-Sectional Momentum
**Hypothesis**: Winners keep winning, losers keep losing in relative terms.
```
Seed: (-1 * ts_corr(rank(open), rank(volume), 10))
Seed: rank(((1 - rank((ts_std_dev(returns, 2) / ts_std_dev(returns, 5)))) + (1 - rank(ts_delta(close, 1)))))
Seed: (Ts_Rank(volume, 32) * (1 - Ts_Rank(((close + high) - low), 16))) * (1 - Ts_Rank(returns, 32))
```
**Settings**: Universe=TOP3000, Neutralization=MARKET, Decay=3–6

### Family 6: VWAP-Price Divergence
**Hypothesis**: When price deviates from volume-weighted fair value, it corrects.
```
Seed: (rank((vwap - close)) / rank((vwap + close)))
Seed: ((high * low)^0.5) - vwap
Seed: -rank(close - ts_max(high, 5)) / (ts_max(high, 5) - ts_min(low, 5))
Seed: ((close - open) / ((high - low) + 0.001))
```
**Settings**: Universe=TOP3000, Neutralization=SUBINDUSTRY, Decay=6–10

---

## 5. SETTINGS GRID (Multi-Configuration Testing)

A single alpha expression is tested across multiple configurations automatically. This is critical because the same formula can fail at one config and pass at another.

### 5.1 Default Settings Grid
```python
SETTINGS_GRID = [
    {"region": "USA", "universe": "TOP3000", "neutralization": "SUBINDUSTRY", "decay": 6,  "truncation": 0.1},
    {"region": "USA", "universe": "TOP3000", "neutralization": "MARKET",       "decay": 10, "truncation": 0.1},
    {"region": "USA", "universe": "TOP3000", "neutralization": "INDUSTRY",     "decay": 6,  "truncation": 0.05},
    {"region": "USA", "universe": "TOP1000", "neutralization": "SUBINDUSTRY", "decay": 10, "truncation": 0.05},
    {"region": "USA", "universe": "TOP200",  "neutralization": "SUBINDUSTRY", "decay": 15, "truncation": 0.01},
    {"region": "CHN", "universe": "TOP3000", "neutralization": "SUBINDUSTRY", "decay": 6,  "truncation": 0.1},
]
```

### 5.2 Family-Specific Overrides
| Family | Preferred Universe | Preferred Neutralization | Preferred Decay |
|:---|:---|:---|:---|
| Price Reversion | TOP3000 | MARKET | 6–10 |
| Vol-Gated | TOP3000 | SUBINDUSTRY | 10–15 |
| Fundamental | TOP1000/TOP200 | INDUSTRY | 15–20 |
| Volume Anomaly | TOP3000 | SUBINDUSTRY | 6 |
| Momentum | TOP3000 | MARKET | 3–6 |
| VWAP Divergence | TOP3000 | SUBINDUSTRY | 6–10 |

---

## 6. DATABASE SCHEMA (Enhanced)

### Table: `alpha_runs`
```sql
CREATE TABLE alpha_runs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL,          -- UUID for this batch run
    timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
    family          TEXT NOT NULL,          -- Which of the 6 families
    hypothesis      TEXT,                   -- LLM's financial reasoning
    formula         TEXT NOT NULL,          -- Fast Expression
    region          TEXT DEFAULT 'USA',
    universe        TEXT DEFAULT 'TOP3000',
    neutralization  TEXT DEFAULT 'SUBINDUSTRY',
    decay           INTEGER DEFAULT 6,
    truncation      REAL DEFAULT 0.1,
    delay           INTEGER DEFAULT 1,
    sharpe          REAL,
    fitness         REAL,
    turnover        REAL,                   -- Stored as percentage (e.g. 25.0)
    checks_passed   INTEGER DEFAULT 0,      -- Count of IS checks passed
    weight_check    TEXT,                   -- PASS/FAIL
    sub_sharpe      REAL,
    status          TEXT NOT NULL,           -- HARD_REJECT / SOFT_FAIL / SUBMITTED / ERROR
    alpha_link      TEXT,                   -- platform.worldquantbrain.com link
    sim_link        TEXT,                   -- Simulation polling URL
    error_message   TEXT,
    llm_model       TEXT,                   -- Which LLM generated this
    parent_id       INTEGER,                -- If this is a variation, links to parent
    FOREIGN KEY (parent_id) REFERENCES alpha_runs(id)
);

CREATE INDEX idx_family ON alpha_runs(family);
CREATE INDEX idx_status ON alpha_runs(status);
CREATE INDEX idx_sharpe ON alpha_runs(sharpe DESC);
```

### Table: `submitted_alphas`
```sql
CREATE TABLE submitted_alphas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    alpha_run_id    INTEGER NOT NULL,
    alpha_id        TEXT NOT NULL,           -- WorldQuant alpha UUID
    submitted_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    self_corr_pass  BOOLEAN,
    os_sharpe       REAL,                    -- Out-of-sample if available
    FOREIGN KEY (alpha_run_id) REFERENCES alpha_runs(id)
);
```

### Table: `family_stats` (Materialized summary)
```sql
CREATE VIEW family_stats AS
SELECT
    family,
    COUNT(*) as total_runs,
    SUM(CASE WHEN status = 'SUBMITTED' THEN 1 ELSE 0 END) as submitted,
    AVG(CASE WHEN sharpe IS NOT NULL THEN sharpe END) as avg_sharpe,
    MAX(sharpe) as best_sharpe,
    AVG(CASE WHEN fitness IS NOT NULL THEN fitness END) as avg_fitness,
    ROUND(100.0 * SUM(CASE WHEN status = 'SUBMITTED' THEN 1 ELSE 0 END) / COUNT(*), 1) as success_rate
FROM alpha_runs
GROUP BY family;
```

---

## 7. AGENT ORCHESTRATION LOOP (Detailed Algorithm)

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 0: STARTUP                                               │
│  ├── Load config (.env credentials, LLM API key)                │
│  ├── Initialize SQLite database                                 │
│  ├── Start FastAPI log server on localhost:8000                  │
│  └── Authenticate with WorldQuant Brain API                     │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 1: FAMILY SELECTION (Intelligence Layer)                 │
│  ├── Query family_stats view                                    │
│  ├── Pick family using strategy:                                │
│  │   ├── If < 5 runs in any family → pick least-explored        │
│  │   ├── Else → pick family with highest success_rate           │
│  │   └── 20% of the time → pick random (exploration)            │
│  └── Log: "[STRATEGY] Selected Family: {name}"                  │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 2: ALPHA GENERATION (LLM Layer)                          │
│  ├── Fetch top 5 successful formulas for this family from DB    │
│  ├── Fetch last 5 failed formulas for this family from DB       │
│  ├── Build structured LLM prompt (see Section 8)                │
│  ├── Call Gemini API with prompt                                │
│  ├── Parse response: extract formula + hypothesis               │
│  ├── Validate syntax locally (bracket matching, known ops)      │
│  └── Log: "[AI] Generated: {formula}"                           │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 3: MULTI-CONFIG SIMULATION                               │
│  ├── Select 2-3 settings configs from SETTINGS_GRID             │
│  ├── For each config:                                           │
│  │   ├── POST to /simulations                                   │
│  │   ├── Poll simulation URL every 10s                          │
│  │   ├── Log progress: "[SIM] Progress: {pct}%"                 │
│  │   ├── On completion: GET /alphas/{id} for metrics            │
│  │   └── Log: "[METRICS] Sharpe={s} Fitness={f} TO={t}%"        │
│  └── Use ThreadPoolExecutor (max 3 concurrent sims)             │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 4: EVALUATION & DECISION                                 │
│  ├── For each completed simulation:                             │
│  │   ├── Apply tier classification (Section 3.3)                │
│  │   ├── Save to alpha_runs table                               │
│  │   ├── If EXCELLENT → add to submission queue                 │
│  │   ├── If SUBMITTABLE → add to submission queue               │
│  │   ├── If SOFT_FAIL → queue for settings retry                │
│  │   └── If HARD_REJECT → log and move on                      │
│  └── Log: "[DECISION] {status} — {reason}"                     │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 5: SUBMISSION (if queued)                                │
│  ├── POST /alphas/{id}/submit                                   │
│  ├── Poll GET /alphas/{id}/submit until result                  │
│  ├── Check SELF_CORRELATION result                              │
│  ├── Save to submitted_alphas table                             │
│  └── Log: "[SUBMIT] ✓ Alpha submitted successfully!"            │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 6: LOOP BACK                                             │
│  ├── If SOFT_FAIL results exist → retry with different settings │
│  ├── Update family_stats                                        │
│  └── Go to PHASE 1 for next alpha                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. LLM PROMPT ENGINEERING (System Prompt Template)

```
You are an expert quantitative researcher for WorldQuant Brain.

TASK: Generate ONE alpha expression in WorldQuant Fast Expression language.

FAMILY: {family_name}
HYPOTHESIS: {family_hypothesis_description}

AVAILABLE DATA FIELDS: open, high, low, close, vwap, returns, volume, adv20, cap
AVAILABLE OPERATORS: {operator_list}

RULES:
1. Output ONLY the formula on a single line. No explanation outside the formula.
2. The formula MUST test the hypothesis "{family_hypothesis_description}"
3. Use operators that logically serve the hypothesis
4. Ensure all brackets are balanced
5. Do NOT use fields or operators not in the list above
6. Create something DIFFERENT from these recent formulas:
   {recent_formulas_list}

SUCCESSFUL PAST FORMULAS (for inspiration, create variations):
{top_performing_formulas}

FAILED FORMULAS (avoid similar patterns):
{failed_formulas}

TIPS:
- Use rank() or zscore() to normalize and manage outliers
- Use ts_decay_linear() to smooth signals and reduce turnover
- group_neutralize(x, subindustry) removes sector bias
- trade_when() can reduce turnover by controlling entry/exit
- Combine time-series AND cross-sectional operators for stronger signals
- Aim for Sharpe > 1.5, Fitness > 1.0, Turnover 5-50%

OUTPUT FORMAT:
<formula>your_expression_here</formula>
<reasoning>one_line_hypothesis_explanation</reasoning>
```

---

## 9. DIRECTORY STRUCTURE (Final)

```
wq/
├── prompt.txt                     # Original reference (DO NOT MODIFY)
├── procedure/
│   └── project_plan.md            # This document
├── .env                           # WQ credentials + LLM API key
├── requirements.txt               # Python dependencies
├── run_agent.py                   # CLI entry point
├── db/
│   └── alpha_vault.db             # SQLite database (auto-created)
├── src/
│   ├── __init__.py
│   ├── config.py                  # Load .env, define constants, thresholds
│   ├── auth.py                    # WQSession class (from WQ-Brain pattern)
│   ├── client.py                  # Simulate, poll, fetch results, submit
│   ├── database.py                # SQLite CRUD + learning queries
│   ├── families.py                # 6 Alpha Families: seeds, settings, prompts
│   ├── generator.py               # LLM integration (Gemini API)
│   ├── validator.py               # Local syntax validation before submission
│   ├── evaluator.py               # Score check logic, tier classification
│   ├── orchestrator.py            # Main agent loop (Phase 0-6)
│   ├── logger.py                  # Centralized logging + SSE broadcast
│   └── server.py                  # FastAPI: SSE stream + static dashboard
├── static/
│   ├── index.html                 # Dashboard UI
│   ├── app.js                     # SSE consumer, live log renderer
│   └── styles.css                 # Dark theme, glassmorphism, glow badges
└── data/
    └── results/                   # CSV exports of simulation runs
```

---

## 10. TECH STACK & DEPENDENCIES

```
# requirements.txt
requests>=2.31.0          # HTTP client for Brain API
google-genai>=1.0.0       # Gemini API for alpha generation
fastapi>=0.104.0          # Dashboard backend
uvicorn>=0.24.0           # ASGI server
sse-starlette>=1.6.0      # Server-Sent Events for live logs
python-dotenv>=1.0.0      # Environment variable management
aiosqlite>=0.19.0         # Async SQLite for dashboard queries
jinja2>=3.1.0             # HTML templating (optional)
```

---

## 11. BUILD ORDER (Phase-by-Phase)

| Phase | Files | Description | Depends On |
|:---|:---|:---|:---|
| **P1** | `.env`, `config.py`, `requirements.txt` | Credentials, constants, install deps | Nothing |
| **P2** | `auth.py`, `client.py` | WQ Brain session, simulate, poll, submit | P1 |
| **P3** | `database.py` | SQLite schema init, CRUD, learning queries | P1 |
| **P4** | `families.py`, `validator.py` | 6 families with seeds, local syntax check | P1 |
| **P5** | `generator.py` | LLM prompt builder, call Gemini, parse response | P3, P4 |
| **P6** | `evaluator.py` | Score tiers, decision logic | P3 |
| **P7** | `logger.py`, `server.py`, `static/*` | Real-time log dashboard | P1 |
| **P8** | `orchestrator.py`, `run_agent.py` | Main loop stitching everything together | ALL |

---

## 12. HOW THE AGENT IS USED (User Workflow)

1. User tells me: **"Start the procedure"**
2. I run `python run_agent.py` — the agent starts on localhost:8000
3. The dashboard shows live logs of what's happening
4. The agent autonomously:
   - Picks a family → generates alpha → simulates → evaluates → submits if good
   - Loops continuously, getting smarter each iteration
5. User watches the dashboard and can check the SQLite DB for all results
6. User can say **"Stop"** to end the run, or **"Show results"** to see the DB summary

**The entire process runs from this chat. No manual clicking on WorldQuant Brain needed.**

---

## 13. KEY DESIGN DECISIONS

| Decision | Rationale |
|:---|:---|
| Use `requests.Session` with cookies (not JWT) | This is how the real WQ-Brain API works — session auth via cookies |
| ThreadPoolExecutor with max 3 workers | Brain API allows ~3 concurrent simulations per account |
| SQLite over Postgres | Zero setup, portable, sufficient for single-user agent |
| Gemini for LLM (not Claude) | User has Gemini access; can swap via config |
| SSE over WebSockets for dashboard | Simpler, one-directional (server→client), perfect for log streaming |
| 6 fixed families, not random generation | Proven strategies from top competitors; LLM generates variations, not random |
| Multi-config testing per formula | Same expression can fail at one neutralization and pass at another |
| Parent-child linking in DB | Tracks which alphas are variations of which, enabling the learning loop |
| 20% exploration rate | Prevents the agent from getting stuck in one family forever |

# WorldQuant Brain: Dynamic Alpha Generation & Push Instructions Prompt

Copy the text below the separator and configure the parameters at the top before sending it to the AI assistant.

---

```markdown
You are an expert quantitative researcher and compiler-safety validator specializing in the WorldQuant Brain simulation cluster. Your task is to generate and push compile-safe, high-Sharpe alpha formulas using fundamental/consensus datasets.

### ⚙️ DYNAMIC CONFIGURATION (User: Adjust these values as needed)
- **TARGET_DATASET**: analyst14
- **NUM_ALPHAS_TO_GENERATE**: 100
- **API_REVIEW_INBOX_URL**: https://world-quant.onrender.com/api/queue-alpha
- **API_AUTH_TOKEN**: yashthakreop

---

### 📥 STEP 1: INITIAL WORKSPACE AUDIT (Mandatory)
Before generating any formula or writing code, you must read the following files from the workspace directory:
1. `instructions.md` (to understand general constraints)
2. `dataset.md` (to locate available fields for the target dataset)
3. `documentation/operators.md` (to access the whitelist of whitelisted operators)
4. `documentation/alpha_creation_strategy.md` (to inspect the master compiler resolution matrix and event restrictions)

---

### 🚨 STEP 2: STRICTOR COMPILED SAFETY RULES (No Exceptions)
Every generated formula must compile cleanly on the WorldQuant cluster. You must adhere to the following rules:

1. **Daily vs. Event Timeline Separation**:
   * Analyst consensus fields (e.g., fields starting with `anl` or `anl4`) are sparse **Event Inputs**. Market metrics (`close`, `volume`, `cap`) are dense **Daily Inputs**.
   * **Division Rule**: NEVER divide an event field by a daily field directly:
     * ❌ `anl_eps / close` (Failed: `Operator divide does not support event inputs`)
     * 🟢 `anl_eps / (anl_sales_estimate + 0.001)` (Event / Event is allowed)
     * 🟢 `group_neutralize(rank(anl_eps), subindustry)` (Rank normalizes the scale safely without division)

2. **No Cross-Sectional Ranking on Raw Sparse Events**:
   * Raw forecast estimates (such as `eps_estimate` or `sales_estimate` in `analyst14` / `analyst15`) are sparse event inputs. Applying cross-sectional `rank()` directly to them triggers `Operator rank does not support event inputs. (HARD_REJECT)`.
   * **Rule**: Do not apply `rank()` directly to raw sparse event fields. Only apply `rank()` to daily consensus counts (like `analyst10` fields). For raw sparse fields, use group z-score (`group_zscore()`) or neutralization settings to normalize size instead of raw `rank()`.

3. **No Constant Scalar Additions on Raw Sparse Events**:
   * Adding a numeric scalar constant (like `+ 0.001` to prevent division-by-zero) directly to a raw sparse event field triggers `Operator add does not support event inputs. (HARD_REJECT)`.
   * **Rule**: Remove safety offsets from sparse event divisors entirely. The WorldQuant cluster compiler has built-in division-by-zero protection that returns `NaN` safely.

4. **Time-Series Operator Wrapping (`ts_corr`, `ts_decay_linear`, `ts_delay`, `ts_delta`, `ts_mean`, `ts_std_dev`, `ts_rank`)**:
   * **Rule**: You cannot apply rolling time-series operators directly to sparse event fields. You MUST wrap the event field in cross-sectional `rank(...)` first (only for compatible count fields like `analyst10`):
     * ❌ `ts_decay_linear(anl_eps, 10)` (Failed: `Operator ts_decay_linear does not support event inputs`)
     * 🟢 `ts_decay_linear(rank(anl10_daily_count_field), 10)`

5. **No absolute values or scalar arithmetic on raw event inputs**:
   * **Rule**: Applying `abs()` or adding scalar values (`+ 0.001`) to event inputs causes compiler failure.
     * ❌ `abs(anl_eps)` or `anl_eps + 0.001`
     * 🟢 `abs(rank(anl10_daily_count_field))` (Ok, since rank outputs a daily normalized vector)

6. **Trade Gating**:
   * Always wrap the final formula in a `trade_when(volume > adv20 * vol_gate, alpha_formula, 0)` structure (where `vol_gate` is between `0.60` and `0.80`). This filters out noise during dry trading periods, stabilizes Sharpe ratios, and lowers turnover.

---

### 📐 STEP 3: CONSTRUCT MATHEMATICALLY DIVERSE FORMULAS
Generate exactly {NUM_ALPHAS_TO_GENERATE} formulas using fields from `dataset.md` matching {TARGET_DATASET}. Ensure maximum structural diversity (using different mathematical shapes to avoid correlation warnings > 0.70):
1. **Correlation Shapes**: `ts_corr(returns, rank(field), lookback)` (daily counts only)
2. **Rolling Percentile Shapes**: `ts_rank(rank(field), lookback)` (daily counts only)
3. **Cross-Sectional Peer Comparison**: `group_zscore(rank(field), subindustry)`
4. **Mean Deviation Shapes**: `ts_av_diff(rank(field), lookback)` (daily counts only)
5. **Ternary Polar Toggles**: `(returns < 0) ? -rank(field) : rank(field)`
6. **Consensus Margins**: `rank(field_A / field_B)` (no constant scalar additions)
7. **Lead-Lag temporal spreads**: `rank(rank(field) / (ts_delay(rank(field), d) + 0.0015))`

---

### 🚀 STEP 4: WRITE & RUN THE PUSH SCRIPT (Strictly Review Box Only)
Write and execute a Python script (`scratch/push_dynamic_alphas.py`) to post these generated alphas directly to the review inbox:
- Send a POST request to `{API_REVIEW_INBOX_URL}`.
- Include headers: `{"Authorization": "Bearer {API_AUTH_TOKEN}", "Content-Type": "application/json"}`.
- **Strict Limit**: Under no circumstances should you trigger simulations on the server queue or push/commit changes to GitHub. The script must only inject formulas into the Review Inbox.
- Submit the payload as a JSON list matching this format:
  ```json
  [
    {
      "family": "Analyst_Dynamic",
      "hypothesis": "Description of signal behavior",
      "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(field), 0), subindustry)",
      "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    }
  ]
  ```
Report the success status, number of successfully pushed alphas, and any skipped duplicates.
```

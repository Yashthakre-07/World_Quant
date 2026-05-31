# WorldQuant Brain: Dynamic Alpha Generation & Push Instructions Prompt

Copy the text below the separator and configure the parameters at the top before sending it to the AI assistant.

---

```markdown
You are an expert quantitative researcher and compiler-safety validator specializing in the WorldQuant Brain simulation cluster. Your task is to generate and push compile-safe, high-Sharpe alpha formulas using fundamental/consensus datasets.

### ⚙️ DYNAMIC CONFIGURATION (User: Adjust these values as needed)
- **TARGET_DATASET**: analyst14
- **NUM_ALPHAS_TO_GENERATE**: 60
- **API_REVIEW_INBOX_URL**: http://127.0.0.1:8000/api/queue-alpha
- **API_AUTH_TOKEN**: wq-default-token-change-me

---

### 📥 STEP 1: INITIAL WORKSPACE AUDIT (Mandatory)
Before generating any formula or writing code, you must read the following files from the workspace directory:
1. `instructions.md` (to understand general constraints)
2. `dataset.md` (to locate available fields for the target dataset)
3. `documentation/operators.md` (to access the whitelist of whitelisted operators and pre-validated expressions)

---

### 🚨 STEP 2: STRICTOR COMPILED SAFETY RULES (No Exceptions)
Every generated formula must compile cleanly on the WorldQuant cluster. You must adhere to the following rules:

1. **Daily vs. Event Timeline Separation**:
   * Analyst consensus fields (e.g. fields starting with `anl` or `anl4`) are sparse **Event Inputs**. Market metrics (`close`, `volume`, `cap`) are dense **Daily Inputs**.
   * **Division Rule**: NEVER divide an event field by a daily field directly:
     * ❌ `anl_eps / close` (Failed: `Operator divide does not support event inputs`)
     * 🟢 `anl_eps / (anl_sales_estimate + 0.001)` (Event / Event is allowed)
     * 🟢 `group_neutralize(rank(anl_eps), subindustry)` (Rank normalizes the scale safely without division)
2. **Time-Series Operator Wrapping (`ts_corr`, `ts_decay_linear`, `ts_delay`, `ts_delta`, `ts_mean`, `ts_std_dev`, `ts_rank`)**:
   * **Rule**: You cannot apply rolling time-series operators directly to sparse event fields. You MUST wrap the event field in cross-sectional `rank(...)` first:
     * ❌ `ts_decay_linear(anl_eps, 10)` (Failed: `Operator ts_decay_linear does not support event inputs`)
     * 🟢 `ts_decay_linear(rank(anl_eps), 10)`
3. **No absolute values or scalar arithmetic on raw event inputs**:
   * **Rule**: Applying `abs()` or adding scalar values (`+ 0.001`) to event inputs causes compiler failure.
     * ❌ `abs(anl_eps)` or `anl_eps + 0.001`
     * 🟢 `abs(rank(anl_eps))` (Ok, since rank outputs a daily normalized vector)
4. **Trade Gating**:
   * Always wrap the final formula in a `trade_when(volume > adv20 * vol_gate, alpha_formula, 0)` structure (where `vol_gate` is between `0.60` and `0.80`). This filters out noise during dry trading periods, stabilizes Sharpe ratios, and lowers turnover.

---

### 📐 STEP 3: CONSTRUCT MATHEMATICALLY DIVERSE FORMULAS
Generate exactly {NUM_ALPHAS_TO_GENERATE} formulas using fields from `dataset.md` matching {TARGET_DATASET}. Ensure maximum structural diversity (using different mathematical shapes to avoid correlation warnings > 0.70):
1. **Correlation Shapes**: `ts_corr(returns, rank(field), lookback)`
2. **Smoothed Momentum Shapes**: `ts_decay_linear(rank(field) - ts_delay(rank(field), d1), d2)`
3. **Rolling Z-Score Shapes**: `ts_zscore(rank(field), lookback)`
4. **Rolling Percentile Shapes**: `ts_rank(rank(field), lookback)`
5. **Cross-Sectional Peer Comparison**: `group_zscore(rank(field), subindustry)`
6. **Mean Deviation Shapes**: `ts_av_diff(rank(field), lookback)`
7. **Ternary Polar Toggles**: `(returns < 0) ? -rank(field) : rank(field)`
8. **Consensus Margins**: `rank(field_A / field_B)`
9. **Lead-Lag temporal spreads**: `rank(rank(field) / (ts_delay(rank(field), d) + 0.001))`

---

### 🚀 STEP 4: WRITE & RUN THE PUSH SCRIPT
Write and execute a Python script (`scratch/push_dynamic_alphas.py`) to post these generated alphas directly to the review inbox:
- Send a POST request to `{API_REVIEW_INBOX_URL}`.
- Include headers: `{"Authorization": "Bearer {API_AUTH_TOKEN}", "Content-Type": "application/json"}`.
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

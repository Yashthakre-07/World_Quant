# ⚡ WorldQuant Brain Agent-Orchestrated Trigger Playbook

> [!IMPORTANT]
> **CRITICAL EXECUTION PROTOCOL**: Whenever the USER invokes the trigger word (e.g. **`start trigger`** or **`run trigger`**) in chat, the Agent must read this playbook ([trigger.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/trigger.md)) and execute the following step-by-step closed-loop sequence. No step, validation check, or reference material scan may be skipped.

---

## 📂 1. THE COMPLETE PIPELINE ECOSYSTEM & FILE REFERENCE

The Agent must be fully aware of the following workspace files and use them to orchestrate the pipeline:

### 🔑 Credentials & Target Specs:
* **[groupa.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/groupa.md)**: Specifications for slots 1–4, Bearer token: `yashthakreop`, target server: `http://localhost:8000` (localhost mode).
* **[groupb.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/groupb.md)**: Specifications for slots 5–8, Bearer token: `yashthakrepro`, target server: `http://localhost:8000` (localhost mode).

### 📚 Mathematical & Compliance Guides:
* **[alpha_generation_guide.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/alpha_generation_guide.md)**: Master guidelines on valid operators, lookback limits (ts_std_dev >= 5, others >= 2), decays (10), delay (1), and universe settings (TOP3000).
* **[instructions.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/instructions.md)**: Details on wrapping event fields inside `vec_avg(field)` and keeping daily matrices (like `model26`, `model135`, `analyst14` `actvalue_*` fields) bare.
* **[expression.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/expression.md)** & **[dataset.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/dataset.md)**: Raw listings of syntax limits, theme mappings, and academic templates.
* **[compiler_error_report_analysis.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/compiler_error_report_analysis.md)**: Historic logs of operator/field conflicts used to populate the blacklist.

### 🛡️ Active Safety & Repair Utilities:
* **[scratch/fix_generated_alphas.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/fix_generated_alphas.py)**: A fail-safe post-generation repair script. Double-checks and enforces unwrapping for continuous daily matrices and wrapping for event vectors.
* **[scratch/fix_local_auth.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/fix_local_auth.py)**: Auto-authenticates and refreshes session tokens using saved cookies when the simulation server returns `HTTP 504 Gateway Timeout` or `HTTP 401 Unauthorized`.
* **[scratch/clear_local_and_resubmit.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/clear_local_and_resubmit.py)**: Overwrites local simulation queues and sends start pipeline triggers.
* **[scratch/show_active_alphas.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/show_active_alphas.py)**: Reads the running backtests from slots 1–8 and prints their active statuses.

### 🗄️ Database, Memory & Whitelist Repositories:
* **[db/alpha_vault.db](file:///c:/Users/Admin/Documents/VIBE_YT/wq/db/alpha_vault.db)**: SQLite database containing all historic runs, metrics (Sharpe, Fitness, Turnover), and error logs.
* **[scratch/discovered_whitelists.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/discovered_whitelists.json)**: Over 800 KB of whitelisted fields, mapped as either `"vectors"` or `"matrices"`.
* **[scratch/elite_templates.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/elite_templates.json)**: High-performance portfolio templates (Sharpe >= 1.5, Fitness >= 1.0) extracted from `alpha_runs` for evolutionary crossover.
* **[scratch/session_memory.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/session_memory.json)**: Tracks global session statistics, cumulative formula blacklists, and field failure lists.

---

## 🛠️ 2. STEP-BY-STEP SEQUENCE PIPELINE (STEPS 0–8)

> [!CAUTION]
> ### 🚨 CRITICAL RULE — NEVER BATCH STEPS TOGETHER
> - **ALWAYS run each step INDIVIDUALLY with a SEPARATE command.**
> - **NEVER use `run_steps_0_4.py` or any batch script to run multiple steps at once.**
> - After EACH step completes, you MUST:
>   1. Print the step output to the terminal
>   2. Immediately write `[STEP X COMPLETED] - <brief summary>` to `live_run.txt`
>   3. READ and CONFIRM the `live_run.txt` was updated before moving to the next step
> - This ensures the agent always has full sequential context and never skips or confuses steps.

For each step, run the script using the absolute Python path:
`C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe scratch/execute_step_<step>.py`

### 🔹 Step 0: Learn from Last Generation + Active Queue Status Report
* **Script**: `scratch/execute_step_0.py`
* **Phase 0-A — Learn from Last Generation** *(runs first)*:
  * Reads `scratch/generation_state.json` and extracts the **previous generation's full results**.
  * Computes and prints key learning insights:
    - Total alphas run, submitted (green), soft-fail, hard-reject, error counts
    - Best Sharpe and average Sharpe of the last generation
    - 🏆 Top alpha formula from last gen (formula, Sharpe, Fitness, Turnover)
    - ⚠️ Top recurring error patterns to avoid repeating
    - 📚 Strategic lessons for the new generation (e.g. "High error rate — fix vec_avg wrappers", "Low Sharpe — try ts_delta normalization")
  * All insights are written to `live_run.txt` for full agent context continuity.
* **Phase 0-B — Active Queue Status Report** *(runs after learning)*:
  * Fetches active slot queues from the remote server.
  * Writes markdown status table to `scratch/slot_status_report.md`.
* **Live Log**: After both phases, writes `[STEP 0 COMPLETED] - Learning from Gen X done. Slot status report written.` to `live_run.txt`.
* **Playbook Integration**: Trigger a queue clear for the selected group's slots (using `scratch/clear_local_and_resubmit.py` logic) to prepare the slots for the fresh run.

### 🔹 Step 1: Blacklist Builder
* **Script**: `scratch/execute_step_1.py`
* **Action**: Scans previous runs and errors to construct the active syntax/field blacklist.

### 🔹 Step 2: Whitelist Field Discovery
* **Script**: `scratch/execute_step_2.py`
* **Action**: Scans `scratch/selected_analyst_fields` and dumps verified variables into `scratch/discovered_whitelists.json`.

### 🔹 Step 3: Anomaly Mapping
* **Script**: `scratch/execute_step_3.py`
* **Action**: Maps whitelisted fields to key academic anomalies (Revision Momentum, Fundamental Accrual).
* **Output**: Writes `scratch/mapped_anomalies.json`.

### 🔹 Step 4: Portfolio Diversity Matrix
* **Script**: `scratch/execute_step_4.py`
* **Action**: Pre-plans the configuration parameters (decays, lookbacks, structures) for the batch.

### 🔹 Step 5: Dual-Agent Alpha Generation & Mutation Loop (AI Orchestered)
Instead of the local offline Python Step 5, the Agent (me) orchestrates this step dynamically:
1. **Prior Generation Load**:
   * Open the previous generation JSON file: `scratch/{group}_generation_{gen-1}.json`.
   * Extract the exact formulas and query `db/alpha_vault.db` for their backtest metrics.
2. **Generator Subagent (`wq_generatorllm`)**:
   * Spawn the `wq_generatorllm` subagent.
   * Provide the target settings (USA, universe: TOP3000, delay: 1, decay: 10, neutralization: SUBINDUSTRY) and the selected whitelisted datasets.
   * Direct it to write `NUM_ALPHAS = <count>` formulas.
3. **Validator Subagent (`wq_validatorllm`)**:
   * Take generator outputs and spawn `wq_validatorllm` to apply volatility scaling (division by standard deviation) and smooth with linear decays.
4. **Post-Agent Repair (`scratch/fix_generated_alphas.py`)**:
   * Run the post-generation repair script over the final formulas to guarantee matrix/vector wrapper compliance.
5. **Write Archive**:
   * Save final formulas to `scratch/generated_alphas.json` and the archive `scratch/{group}_generation_{gen}.json`.
   * Increment generation count in `scratch/generation_state.json`.

### 🔹 Step 6: Uniqueness Checks
* **Script**: `scratch/execute_step_6.py`
* **Action**: Prevents duplicate submissions by comparing formulas against local and database records. Auto-regenerates duplicates.

### 🔹 Step 7: Pairwise Correlation Check
* **Script**: `scratch/execute_step_7.py`
* **Action**: Validates that cross-alpha correlation is strictly $< 0.70$.

### 🔹 Step 8: Final Validation, Queue Submission & Memory Update
* **Script**: `scratch/execute_step_8.py` and `scratch/show_active_alphas.py`
* **Action**: Evaluates all alphas against operator compliance rules using `validate_fastexpr` (specifically checking for valid/allowed operators and whitelisted fields). Aborts submission if any invalid operator is detected. Otherwise, dynamically retrieves the Bearer token based on the selected group, overwrites the local simulation queue on `localhost:8000` via POST to `/api/overwrite-queue`, triggers the local pipeline start, and logs the submitted formulas and outcome matrices to `scratch/session_memory.json`.
* **Playbook Integration**: Query the `/api/status` endpoint to verify that the newly submitted alphas are actively in the queue and simulating. Once verified, write the absolute final line to `live_run.txt` containing exactly: `Haan, they are stimulating.`

---

## 📊 3. UNIFIED LOGGING & TIMEOUT PROTECTION
* **Resetting Logs**: At the very beginning of the trigger run, the Agent must clear [live_run.txt](file:///c:/Users/Admin/Documents/VIBE_YT/wq/live_run.txt) entirely to avoid context drift.
* **Step-by-Step Reporting**: After each step completes, write a clear confirmation message containing `[STEP <X> COMPLETED]` and a brief summary of results directly to [live_run.txt](file:///c:/Users/Admin/Documents/VIBE_YT/wq/live_run.txt).
  - *Example*: `[STEP 1 COMPLETED] - Blacklist successfully compiled.`
* **Step 5 Alpha Tracking**: During Step 5, the Agent must print the exact generated and validated alphas (formulas and hypotheses) to [live_run.txt](file:///c:/Users/Admin/Documents/VIBE_YT/wq/live_run.txt) with headers `[GENERATED ALPHAS]` and `[VALIDATED/MUTATED ALPHAS]` to ensure context transparency.
* **Continuous State Enforcement**: Keep track of the current step index dynamically inside [scratch/pipeline_state.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/pipeline_state.json) so execution can resume cleanly if interrupted.
* **Authentication Watcher**: If any connection check throws an auth failure, immediately execute **`scratch/fix_local_auth.py`** to refresh cookies and restore active session state before continuing the steps.

---

## 🛡️ 4. WQ CLUSTER COMPLIANCE RULES TO PREVENT CHILD SIMULATION FAILURES
To ensure child simulations do not fail on the WorldQuant cluster, future generation cycles must adhere to these structural compliance rules:
* **Vector Field Wrapping**:
  - *Rule*: All analyst consensus and actual event fields (such as `anl4`, `anl14`, `anl15`, `anl45`, etc.) are sparse, event-driven vector fields on WQ.
  - *Action*: They **must** be wrapped in `vec_avg(field)` before any mathematical operators (addition, subtraction, division, or standard deviation) are applied to them.
  - *Example*: Use `ts_std_dev(vec_avg(anl14_actvalue_capex_fy0), 20)` instead of `ts_std_dev(anl14_actvalue_capex_fy0, 20)`.
* **Divisor Stability & Zero/NaN Protection**:
  - *Rule*: Standard deviation operators (`ts_std_dev(field, N)`) used as divisors can evaluate to `0` or `NaN` when applied to sparse variables or early years, crashing sub-simulations.
  - *Action*: Always add a non-zero constant offset to standard deviation divisors: `(ts_std_dev(vec_avg(field), N) + 0.001)`. Avoid using standard deviations as divisors on sparse event fields unless necessary.



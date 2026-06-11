# GROUP A AUTOMATION HANDOFF & RESUMPTION PROTOCOL

> [!CAUTION]
> **CRITICAL CONSTRAINTS:**
> - **NO GITHUB PUSH**: Never trigger, run, or perform any git push commands under any circumstances.
> - **NO BIOMETRIC TRIGGER**: Never trigger or generate biometric verification/Persona flows.

This document outlines the exact state-machine architecture, credentials, target parameters, and command execution mappings for **Group A** slots. When instructed to **"start groupa.md"**, read this file and resume automated execution immediately.

---

## 🔑 1. ENVIRONMENT CONFIGURATION & CREDENTIALS
- **Target Slots**: 1, 2, 3, 4 (strictly slots 1–4, never touch slots 5–8)
- **API Target Server**: `https://world-quant.onrender.com`
- **Bearer Token**: `yashthakreop`
- **Headers**:
  ```json
  {
    "Authorization": "Bearer yashthakreop",
    "Content-Type": "application/json"
  }
  ```
- **Portfolio Size**: 40 alphas (10 per slot)
- **Queue Management Mode**: Overwrite mode (using POST to `/api/overwrite-queue` to maintain exactly 40 alphas)

---

## ⚙️ 2. STATE-MACHINE SYSTEM ARCHITECTURE
- **State File**: [scratch/pipeline_state.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/pipeline_state.json) tracks `"current_step"`.
- **Generation File**: [scratch/generation_state.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/generation_state.json) tracks the active `"current_generation"` and stores performance history.
- **Scheduled Trigger**: Run every 15 minutes using the scheduler tool:
  - `CronExpression`: `*/15 * * * *`
  - `Prompt`: `"Start the pipeline execution cycle: read master prompt files step 0 to 10 and process them for slots 1-4."`
- **Step Transitions**: After executing the Python command for the current step, the system:
  1. Increments `"current_step"` in `scratch/pipeline_state.json`.
  2. Schedules a **one-shot 5-second timer** using the `schedule` tool to wake itself up for the next step.
  3. Pauses until the timer fires to guarantee zero-hallucination execution.
  4. Resets `"current_step"` to `0` after Step 10 completes.
- **Closed-Loop Mutator**: Step 5 dynamically loads the generation state file, queries the backtest results database (`db/alpha_vault.db`) for the last generation, mutates formulas based on performance feedback, and advances to the next targeted generation.

---

## 🛠️ 3. STEP COMMAND MAPPING
For each state, run the corresponding Python script using `C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe` in `c:\Users\Admin\Documents\VIBE_YT\wq`:

| Step # | Script Path | Description |
| :---: | :--- | :--- |
| **Step 0** | [scratch/execute_step_0.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_0.py) | Fetch server status, filter slots 1–4, write report to `scratch/slot_status_report.md` |
| **Step 1** | [scratch/execute_step_1.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_1.py) | Scan compiler errors and compile master blacklist |
| **Step 2** | [scratch/execute_step_2.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_2.py) | Discover whitelisted fields on analyst4, analyst14, analyst45 |
| **Step 3** | [scratch/execute_step_3.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_3.py) | Map fields to academic anomalies |
| **Step 4** | [scratch/execute_step_4.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_4.py) | Create 40-alpha diversity matrix |
| **Step 5** | [scratch/execute_step_5.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_5.py) | **AI Generation**: Spawn `wq_generatorllm` to design candidate formulas and `wq_validatorllm` to validate, scale, and fix compliance before archiving. |
| **Step 6** | [scratch/execute_step_6.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_6.py) | Check uniqueness against historical databases |
| **Step 7** | [scratch/execute_step_7.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_7.py) | Estimate pairwise correlations (target < 0.70) |
| **Step 8** | [scratch/execute_step_8.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_8.py) | Run settings check and 12-point final validation checklist |
| **Step 9** | [scratch/execute_step_9.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_9.py) | POST overwrite array payload to `https://world-quant.onrender.com/api/overwrite-queue` |
| **Step 10** | [scratch/execute_step_10.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_10.py) | Update self-improvement logs in `scratch/session_memory.json` |

---

## ⚡ 4. RESUMPTION COMMANDS
To start the pipeline, trigger the recurring cron job via:
```powershell
# In scheduler tool:
CronExpression = "*/15 * * * *"
Prompt = "Start the pipeline execution cycle: read master prompt files step 0 to 10 and process them for slots 1-4."
```
Verify `scratch/pipeline_state.json` is set to `"current_step": 0` before initiating.

---

## 🛡️ 5. WQ CLUSTER COMPLIANCE RULES TO PREVENT CHILD SIMULATION FAILURES
* **Vector Field Wrapping**: All analyst consensus/actual event fields (e.g. `anl4`, `anl14`, `anl15`, `anl45`) are event-driven vector fields on WQ and **must** be wrapped in `vec_avg(field)` before applying mathematical operations (add, subtract, divide, ts_std_dev).
  - *Example*: Use `ts_std_dev(vec_avg(anl14_actvalue_capex_fy0), 20)` instead of `ts_std_dev(anl14_actvalue_capex_fy0, 20)`.
* **Divisor Stability**: Standard deviation divisors (`ts_std_dev(field, N)`) can evaluate to `0` or `NaN` on sparse data, causing child simulations to fail. Always add a non-zero offset: `(ts_std_dev(vec_avg(field), N) + 0.001)`.


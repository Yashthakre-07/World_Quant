# Group B Automated Execution Protocol

> [!CAUTION]
> **CRITICAL CONSTRAINTS:**
> - **NO GITHUB PUSH**: Never trigger, run, or perform any git push commands under any circumstances.
> - **NO BIOMETRIC TRIGGER**: Never trigger or generate biometric verification/Persona flows.

This document defines the configuration, specifications, and state machine process flow for **Group B**. If requested to start, restore, or run Group B, execute the exact actions below.

---

## ⚙️ Target Parameters
* **Target Slots:** Slots 5, 6, 7, and 8 (Never impact Slots 1–4).
* **Python Interpreter Path:** `C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe`
* **Server Target (Status):** `https://world-quant.onrender.com/api/status`
* **Server Target (Submission):** `https://world-quant.onrender.com/api/overwrite-queue`
* **Authorization Header:** `Bearer yashthakrepro`
* **Batch Size:** 40 Alphas (10 per slot)
* **Queue Mode:** Full Overwrite via POST

---

## 🔁 State Machine Configuration
The execution state is managed in [pipeline_state.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/pipeline_state.json) using the format:
```json
{
  "current_step": 0
}
```

### Execution Cycle Actions:
1. Read the `current_step` from `scratch/pipeline_state.json`.
2. Run the corresponding step script using the absolute python path:
   ```cmd
   C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe scratch/execute_step_<current_step>.py
   ```
3. Write the next step (incremented by 1, wrapping to 0 after step 10) back to `scratch/pipeline_state.json`.
4. Schedule a 5-second one-shot timer to trigger the next step immediately.
5. Once Step 10 completes, go idle until the next 10-minute cron interval triggers.

---

## 📋 Steps Specification

| Step | Script Path | Description |
| :--- | :--- | :--- |
| **0** | [execute_step_0.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_0.py) | **Status Report**: Fetch queue status, filter for slots `[5, 6, 7, 8]`, and write to `scratch/slot_status_report.md`. |
| **1** | [execute_step_1.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_1.py) | **Blacklist**: Build the syntax/operator blacklist. |
| **2** | [execute_step_2.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_2.py) | **Field Discovery**: Discover whitelisted vector/matrix fields. |
| **3** | [execute_step_3.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_3.py) | **Anomaly Map**: Map 15 quantitative trading anomalies. |
| **4** | [execute_step_4.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_4.py) | **Diversity Matrix**: Pre-plan portfolio configuration. |
| **5** | [execute_step_5.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_5.py) | **Formula Generation**: Generate 40 unique alphas with `vec_avg()` wrappers. |
| **6** | [execute_step_6.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_6.py) | **Uniqueness**: Filter duplicate formulas. |
| **7** | [execute_step_7.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_7.py) | **Correlation**: Verify pairwise correlation is below 0.70. |
| **8** | [execute_step_8.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_8.py) | **Validation**: Run the 12-point checklist. |
| **9** | [execute_step_9.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_9.py) | **Submission**: Submit/overwrite payload to the `overwrite-queue` endpoint. |
| **10**| [execute_step_10.py](file:///c:/Users/Admin/Documents/VIBE_YT/wq/scratch/execute_step_10.py) | **Memory Update**: Append formulas and metrics to `session_memory.json`. |

---

## 🚀 How to Start / Resume Group B
To trigger the automated cycle:
1. Initialize/reset `scratch/pipeline_state.json` to step `0`.
2. Schedule a recurring cron job using the `schedule` tool:
   * **Interval:** `*/15 * * * *` (Every 15 minutes)
   * **Prompt:** `Execute the next step of the Group B state machine. Read scratch/pipeline_state.json, run the corresponding python script, update the step, and set a 5-second one-shot timer for the next step.`

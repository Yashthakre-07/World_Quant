# TASK: GRAB ALPHAS FROM PIPELINE AND GENERATE SLOT STATUS REPORT

Connect to our active pipeline server, retrieve all currently executing/pending alphas, filter them strictly by the targeted slots, and generate a markdown status report without modifying any queues.

---

## 1. SERVER ACCESS CREDENTIALS
Use the following configurations to query the server:

- FOR SLOTS 1-4 (Group A):
  - API URL: https://world-quant.onrender.com/api/status
  - Headers: {"Authorization": "Bearer yashthakreop", "Content-Type": "application/json"}

- FOR SLOTS 5-8 (Group B):
  - API URL: https://world-quant-1.onrender.com/api/status
  - Headers: {"Authorization": "Bearer yashthakrepro", "Content-Type": "application/json"}

---

## 2. STEP-BY-STEP WORKFLOW

### STEP 1: Fetch Alphas from Queue
1. Make an authenticated HTTP GET request to the target server's `/api/status` endpoint using the corresponding headers.
2. Read the list of alphas from the `alphas` key in the JSON response payload.

### STEP 2: Filter by Target Slots
Filter the list of alphas strictly by `slot_id`:
- If targeting Group A: Filter for alphas where `slot_id` is 1, 2, 3, or 4.
- If targeting Group B: Filter for alphas where `slot_id` is 5, 6, 7, or 8.
*Ensure that you do not alter, touch, or process alphas assigned to other slot IDs.*

### STEP 3: Generate the Status Report
Save a markdown report to `scratch/slot_status_report.md` with the following structure:

### 📊 Slot Status Report (Targeted Slots)
**Timestamp**: [Insert current local ISO time]
**Target Server**: [Insert queried URL]
**Total Target Alphas**: [Count of filtered alphas]

| Slot ID | Status | Progress | Sharpe | Fitness | Turnover | Formula |
|---|---|---|---|---|---|---|
| [Slot #] | [e.g., SIMULATING] | [N]% | [Sharpe] | [Fitness] | [Turnover] | `[formula]` |

---

## 3. CORE CONSTRAINT
This task is READ-ONLY. Do not call any modifying endpoints (such as `/api/clear-queue`, `/api/overwrite-queue`, or `/api/purge-vault`). You must only retrieve queue data.

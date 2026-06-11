step 9

STEP 9 — SUBMISSION TO REVIEW BOX
══════════════════════════════════
READ THIS STEP FULLY. COMPLETE IT FULLY. THEN STOP AND PRINT:
✅ STEP 9 COMPLETE — ALL ALPHAS SUBMITTED
══════════════════════════════════
YOUR TASK IN STEP 9:
Submit every validated alpha to the Review Box API. Every alpha must be submitted. Count must match NUM_ALPHAS exactly.

API DETAILS:

Endpoint: https://world-quant.onrender.com/api/queue-alpha
Method: POST
Headers:
  Authorization: Bearer yashthakreop
  Content-Type: application/json
PAYLOAD FORMAT (one object per alpha):
json

[
  {
    "family": "[anomaly family e.g. EPS_REVISION_MOMENTUM]",
    "dataset": "[dataset name e.g. analyst4]",
    "competition": "IQC2025",
    "hypothesis": "[one sentence economic rationale]",
    "anomaly_basis": "[academic anomaly name from Step 3]",
    "formula": "[the validated formula string]",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": [N],
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  }
]
PRE-SUBMISSION COUNT VERIFICATION:

PRE-SUBMISSION CHECK:
  NUM_ALPHAS configured: [N]
  Alphas generated: [N]
  Alphas validated: [N]
  Alphas in payload: [N]
  All counts match: YES / NO
If any count mismatch → ABORT. Do not submit partial batches.

SUBMISSION LOOP:
For each alpha, submit individually. Log every attempt:


SUBMITTING ALPHA [N]: [formula preview]
  HTTP Status: [200 / error code]
  Response: [response body]
  Result: SUCCESS ✅ / FAILED ❌
ERROR HANDLING:
HTTP 200 → Success, continue
HTTP 4xx → Log error body, stop, do not retry blind
HTTP 5xx → Log error, wait 30 seconds, retry once
Connection error → Save all alphas to scratch/failed_submission.json, log failure
FINAL SUBMISSION REPORT:

SUBMISSION REPORT:
  Total submitted: [N]
  Total succeeded: [N]
  Total failed: [N]
  Failed alpha indices: [list if any]
If total succeeded < NUM_ALPHAS → save unsent alphas to scratch/failed_submission.json for retry next session.

PYTHON SUBMISSION SCRIPT (run if API call fails from here):
C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe push_accepted_alphas.py --num-alphas [N]
Do NOT use --dry-run flag in production.

✅ STEP 9 COMPLETE — ALL ALPHAS SUBMITTED

══════════════════════════════════

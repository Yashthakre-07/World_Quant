"""
=============================================================
  LOCAL TEST PIPELINE — ALL 8 SLOTS (TEMP / TODAY ONLY)
=============================================================
  - Targets: http://localhost:5000  (NOT Render)
  - Controls: Slots 1-4 (Group A) + Slots 5-8 (Group B)
  - Merged into a single run loop
  - Token A = yashthakreop  (slots 1-4)
  - Token B = yashthakrepro (slots 5-8)

  Run this AFTER starting the local server:
      python run_pipeline.py

  Usage:
      python scratch/run_local_all8.py
      python scratch/run_local_all8.py --loop   (keeps repeating)
=============================================================
"""

import json
import subprocess
import sys
import os
import time
import urllib.request
import urllib.error
import argparse

# ── Config ─────────────────────────────────────────────────
LOCAL_BASE_URL    = "http://localhost:8000"
TOKEN_A           = "yashthakreop"   # Group A — slots 1-4
TOKEN_B           = "yashthakrepro"  # Group B — slots 5-8
PYTHON            = sys.executable
STATE_PATH        = "scratch/pipeline_state.json"
GEN_STATE_PATH    = "scratch/generation_state.json"
ALPHAS_PATH       = "scratch/generated_alphas.json"
SESSION_MEM_PATH  = "scratch/session_memory.json"
SYNC_SCRIPT       = "developer/scratch_sync_vault_to_local.py"

BANNER = """
+----------------------------------------------------------+
|   LOCAL ALL-8-SLOT PIPELINE  -  http://localhost:8000   |
+----------------------------------------------------------+
"""


# ── Helpers ─────────────────────────────────────────────────
def log(msg):
    ts = time.strftime("%H:%M:%S")
    # Encode safely for Windows terminals that don't support full unicode
    safe_msg = msg.encode("ascii", errors="replace").decode("ascii")
    print(f"[{ts}] {safe_msg}", flush=True)

def separator(label=""):
    bar = "=" * 60
    safe_label = label.encode("ascii", errors="replace").decode("ascii")
    if safe_label:
        print(f"\n{bar}\n  {safe_label}\n{bar}")
    else:
        print(f"\n{bar}")

def api_get(path, token=TOKEN_A):
    url = LOCAL_BASE_URL + path
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8")), r.getcode()
    except urllib.error.URLError as e:
        return None, str(e)

def api_post(path, payload=None, token=TOKEN_A):
    url = LOCAL_BASE_URL + path
    data = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8")), r.getcode()
    except urllib.error.URLError as e:
        return None, str(e)


# ── Server health check ─────────────────────────────────────
def wait_for_server(max_wait=60):
    log(f"Checking local server at {LOCAL_BASE_URL} ...")
    for i in range(max_wait):
        try:
            with urllib.request.urlopen(LOCAL_BASE_URL + "/api/status", timeout=5) as r:
                if r.getcode() == 200:
                    log("[OK] Local server is UP!")
                    return True
        except Exception:
            pass
        if i == 0:
            log("Server not ready yet, waiting...")
        time.sleep(1)
    log("[ERROR] Server did not come up in time. Make sure you ran: python run_pipeline.py")
    return False


# ── Slot status printer ─────────────────────────────────────
def print_slot_status():
    separator("CURRENT SLOT STATUS (All 8)")
    data_a, _ = api_get("/api/status", TOKEN_A)
    data_b, _ = api_get("/api/status", TOKEN_B)

    def print_slots(data, label, slot_range):
        if not data or "alphas" not in data:
            log(f"  [{label}] No data returned")
            return
        alphas = [a for a in data["alphas"] if a.get("slot_id") in slot_range]
        for a in alphas:
            slot     = a.get("slot_id", "?")
            status   = a.get("status", "?")
            sharpe   = a.get("sharpe", "N/A")
            fitness  = a.get("fitness", "N/A")
            turnover = a.get("turnover", "N/A")
            formula  = str(a.get("formula", ""))[:60]
            print(f"  Slot {slot} [{label}] | {status:15s} | Sharpe={sharpe} | Fit={fitness} | Turn={turnover}")
            print(f"    Formula: {formula}...")

    print_slots(data_a, "GROUP-A", {1, 2, 3, 4})
    print_slots(data_b, "GROUP-B", {5, 6, 7, 8})


# ── Sync vault from remote ─────────────────────────────────
def sync_vault():
    separator("SYNCING VAULT → LOCAL DB")
    if os.path.exists(SYNC_SCRIPT):
        result = subprocess.run([PYTHON, SYNC_SCRIPT], capture_output=True, text=True, encoding="utf-8")
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        log("Vault sync done.")
    else:
        log(f"Sync script not found at {SYNC_SCRIPT} — skipping.")


# ── Run the 11-step generation pipeline ────────────────────
def safe_print(text):
    """Print text safely on Windows terminals that don't support full Unicode."""
    safe = text.encode("ascii", errors="replace").decode("ascii")
    print(safe)

def run_step(step_idx):
    script = f"scratch/execute_step_{step_idx}.py"
    if not os.path.exists(script):
        log(f"Script not found: {script}")
        return False

    log(f"-> Running Step {step_idx} ...")
    result = subprocess.run([PYTHON, script], capture_output=True, text=True, encoding="utf-8")
    safe_print(result.stdout)
    if result.stderr:
        safe_print("STDERR: " + result.stderr)

    if result.returncode != 0:
        log(f"[FAIL] Step {step_idx} FAILED (exit code {result.returncode})")
        return False

    log(f"[OK] Step {step_idx} done.")
    return True


def run_generation_pipeline():
    """Run steps 0-10 locally (generate + mutate alphas)."""
    separator("GENERATION PIPELINE (Steps 0–10)")

    # Load start step
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            start_step = json.load(f).get("current_step", 0)
    except Exception:
        start_step = 0

    # Read current generation
    try:
        with open(GEN_STATE_PATH, "r", encoding="utf-8") as f:
            gen = json.load(f).get("current_generation", "?")
    except Exception:
        gen = "?"

    log(f"Starting from step {start_step} | Generation = {gen}")

    for step in range(start_step, 11):
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump({"current_step": step}, f)

        ok = run_step(step)
        if not ok:
            log(f"Pipeline halted at step {step}.")
            return False

        next_step = 0 if step == 10 else step + 1
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump({"current_step": next_step}, f)

        time.sleep(1)

    log("All 11 steps complete.")
    return True


# ── Push alphas to LOCAL server for BOTH groups ────────────
def push_to_local_all8():
    """
    Push the generated_alphas.json to the LOCAL server.
    First 4 alphas → Group A (slots 1-4) via TOKEN_A
    Last 4 alphas  → Group B (slots 5-8) via TOKEN_B
    """
    separator("PUSHING ALPHAS → LOCALHOST (All 8 Slots)")

    try:
        with open(ALPHAS_PATH, "r", encoding="utf-8") as f:
            alphas = json.load(f)
    except Exception as e:
        log(f"❌ Cannot read generated_alphas.json: {e}")
        return False

    # Build payloads
    def make_payload(alpha):
        return {
            "family":        alpha["family"],
            "dataset":       alpha["dataset"],
            "competition":   "IQC2025",
            "hypothesis":    alpha["hypothesis"],
            "anomaly_basis": alpha["anomaly_basis"],
            "formula":       alpha["formula"],
            "settings": {
                "region":         "USA",
                "delay":          1,
                "decay":          alpha.get("decay", 10),
                "neutralization": "SUBINDUSTRY",
                "universe":       "TOP3000",
                "truncation":     0.08
            }
        }

    group_a_payload = [make_payload(a) for a in alphas[:8]]
    group_b_payload = [make_payload(a) for a in alphas[8:16]]

    # Push Group A → slots 1-4 (8 alphas, 2 per slot)
    log(f"Pushing {len(group_a_payload)} alphas to GROUP-A (slots 1-4) -> {LOCAL_BASE_URL}/api/overwrite-queue")
    resp_a, code_a = api_post("/api/overwrite-queue", group_a_payload, TOKEN_A)
    if code_a == 200:
        log("[OK] Group A push SUCCESS")
    else:
        log(f"[FAIL] Group A push FAILED -- HTTP {code_a} | {resp_a}")

    time.sleep(1)

    # Push Group B → slots 5-8 (8 alphas, 2 per slot)
    log(f"Pushing {len(group_b_payload)} alphas to GROUP-B (slots 5-8) -> {LOCAL_BASE_URL}/api/overwrite-queue")
    resp_b, code_b = api_post("/api/overwrite-queue", group_b_payload, TOKEN_B)
    if code_b == 200:
        log("[OK] Group B push SUCCESS")
    else:
        log(f"[FAIL] Group B push FAILED -- HTTP {code_b} | {resp_b}")

    # Trigger pipeline start on local server
    log("Triggering /api/start-pipeline on local server ...")
    _, sc_a = api_post("/api/start-pipeline", {}, TOKEN_A)
    _, sc_b = api_post("/api/start-pipeline", {}, TOKEN_B)
    log(f"  Group A start: {sc_a} | Group B start: {sc_b}")

    return True


# ── Full cycle ──────────────────────────────────────────────
def run_full_cycle():
    print(BANNER)

    if not wait_for_server():
        print("\n💡 Start the local server first:\n   python run_pipeline.py\n")
        sys.exit(1)

    # 1. Show current slot status
    print_slot_status()

    # 2. Sync latest results from remote vault
    sync_vault()

    # 3. Run the generation pipeline (steps 0-10)
    ok = run_generation_pipeline()
    if not ok:
        log("Generation pipeline failed. Check errors above.")
        return

    # 4. Push all 8 slots to localhost
    push_to_local_all8()

    # 5. Final slot status
    time.sleep(3)
    print_slot_status()

    separator("CYCLE COMPLETE")
    log("Done! Monitor results at: http://localhost:5000")


# ── Entry point ─────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local all-8-slot test pipeline")
    parser.add_argument("--loop", action="store_true",
                        help="Keep repeating the cycle indefinitely")
    parser.add_argument("--interval", type=int, default=300,
                        help="Seconds between loops (default: 300)")
    parser.add_argument("--status-only", action="store_true",
                        help="Just print slot status and exit")
    parser.add_argument("--push-only", action="store_true",
                        help="Skip generation, just push last generated_alphas.json to localhost")
    args = parser.parse_args()

    if args.status_only:
        if not wait_for_server(max_wait=10):
            sys.exit(1)
        print_slot_status()
        sys.exit(0)

    if args.push_only:
        if not wait_for_server(max_wait=10):
            sys.exit(1)
        push_to_local_all8()
        sys.exit(0)

    if args.loop:
        cycle = 0
        while True:
            cycle += 1
            separator(f"LOOP CYCLE #{cycle}")
            run_full_cycle()
            log(f"Waiting {args.interval}s before next cycle... (Ctrl+C to stop)")
            time.sleep(args.interval)
    else:
        run_full_cycle()

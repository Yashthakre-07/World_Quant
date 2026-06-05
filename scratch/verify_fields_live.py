import requests
import json
import urllib3
import time
import sys

urllib3.disable_warnings()

PUSH_URL = "https://world-quant.onrender.com/api/queue-alpha"
STATUS_URL = "https://world-quant.onrender.com/api/status"
CLEAR_URL = "https://world-quant.onrender.com/api/clear-queue"
INJECT_URL = "https://world-quant.onrender.com/api/inject-inbox"

HEADERS = {
    "Authorization": "Bearer yashthakreop",
    "Content-Type": "application/json"
}

def verify_variables(variables_list):
    """
    Constructs safe test alphas for each variable, pushes to queue,
    triggers simulation, and polls status to find allowed vs un-subscribed fields.
    """
    print(f"[*] Starting live verification of {len(variables_list)} variables...")
    
    # 1. Clear remote queue first
    requests.post(CLEAR_URL, headers=HEADERS, verify=False)
    
    # 2. Build test formulas. Since we don't know if a field is vector or matrix,
    # we can use ts_backfill(x, 252) which is highly tolerant and works for both event and matrix!
    # Or try simple: group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_backfill(x, 252)), 0), subindustry)
    # wait, ts_backfill is allowed on both matrices and vectors on WQ.
    test_alphas = []
    for var in variables_list:
        # Construct formula that is compiler-safe for both event/matrix
        formula = f"group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_backfill({var}, 252)), 0), subindustry)"
        test_alphas.append({
            "family": "verification_test",
            "hypothesis": f"Verify variable: {var}",
            "formula": formula,
            "settings": {
                "region": "USA",
                "delay": 1,
                "decay": 8,
                "neutralization": "SUBINDUSTRY",
                "universe": "TOP3000",
                "truncation": 0.08
            }
        })
        
    # 3. Push to queue
    print(f"[*] Pushing {len(test_alphas)} test formulas to Review API...")
    r = requests.post(PUSH_URL, json=test_alphas, headers=HEADERS, verify=False)
    if r.status_code != 200:
        print(f"[ERROR] Push failed: {r.status_code} - {r.text}")
        return
        
    print("[SUCCESS] Test formulas successfully pushed.")
    
    # 4. Trigger inject
    print("[*] Injecting into simulation queue...")
    r = requests.post(INJECT_URL, json={"all": True}, headers=HEADERS, verify=False)
    if r.status_code != 200:
        print(f"[ERROR] Injection failed: {r.status_code} - {r.text}")
        return
        
    # 5. Poll status until done or max wait (e.g. 90 seconds)
    print("[*] Waiting for compiler evaluation (polling status)...")
    max_attempts = 15
    for attempt in range(max_attempts):
        time.sleep(8)
        r = requests.get(STATUS_URL, verify=False)
        if r.status_code != 200:
            print(f"[ERROR] Failed to fetch status: {r.status_code}")
            continue
            
        data = r.json()
        alphas = data.get("alphas", [])
        
        # Check if all tested alphas are done (status is not 'QUEUED' or 'SIMULATING' or None)
        active_alphas = [a for a in alphas if a.get("family") == "verification_test"]
        if not active_alphas:
            print("[*] No active verification alphas in queue. Waiting...")
            continue
            
        pending = sum(1 for a in active_alphas if a.get("status") in ["QUEUED", "SIMULATING", None])
        print(f"  Attempt {attempt+1}/{max_attempts}: {len(active_alphas) - pending}/{len(active_alphas)} evaluated...")
        
        if pending == 0:
            print("[SUCCESS] All test formulas evaluated.")
            break
            
    # 6. Analyze results
    r = requests.get(STATUS_URL, verify=False)
    alphas = r.json().get("alphas", [])
    active_alphas = [a for a in alphas if a.get("family") == "verification_test"]
    
    allowed = []
    unsubscribed = []
    other_errors = []
    
    for a in active_alphas:
        formula = a.get("formula")
        # Extract variable name from formula
        var = formula.split("ts_backfill(")[1].split(",")[0].strip()
        status = a.get("status")
        err = a.get("error_message") or ""
        
        if status in ["ERROR", "HARD_REJECT"] and "unknown variable" in err.lower():
            unsubscribed.append(var)
        elif status in ["ERROR", "HARD_REJECT"] and "does not exist" in err.lower():
            unsubscribed.append(var)
        elif status in ["ERROR", "HARD_REJECT"]:
            # If it's a different error, the variable might be allowed but there's a math syntax/compilation issue
            allowed.append(var)
            other_errors.append((var, err))
        else:
            # Compiled successfully (SIMULATING, GREEN, SOFT_FAIL, etc.)
            allowed.append(var)
            
    print("\n" + "="*40)
    print("LIVE VERIFICATION RESULTS:")
    print("="*40)
    print(f"Allowed Variables ({len(allowed)}):")
    for v in allowed:
        print(f"  [PASS] {v}")
    print(f"\nUn-subscribed Variables ({len(unsubscribed)}):")
    for v in unsubscribed:
        print(f"  [FAIL] {v}")
        
    if other_errors:
        print(f"\nOther Errors ({len(other_errors)}):")
        for v, e in other_errors:
            print(f"  [{v}] {e}")

if __name__ == "__main__":
    # Get variables to test from command line
    if len(sys.argv) > 1:
        test_vars = sys.argv[1:]
    else:
        # Default test variables if none provided
        test_vars = [
            "anl4_fs_basic_splt_v4_nd_eps_estimate",
            "anl4_afv4_eps_mean",
            "anl14_actvalue_eps_fp0",
            "anl14_mean_sales_fp1",
            "anl44_analyst",
            "anl45_ad_rel_ret_per"
        ]
    verify_variables(test_vars)

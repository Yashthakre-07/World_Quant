import urllib.request
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    tokens = [("yashthakreop", "GROUP A"), ("yashthakrepro", "GROUP B")]
    
    print("==========================================")
    # Fetch and show simulation results on localhost
    print("ACTIVE SIMULATION RESULTS ON LOCALHOST")
    print("==========================================\n")
    
    total_active = 0
    simulating_count = 0
    passed_count = 0
    soft_fail_count = 0
    failed_count = 0
    
    for token, group_name in tokens:
        url = "http://localhost:8000/api/status"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode("utf-8"))
                alphas = data.get("alphas", [])
                
                print(f"--- {group_name} ---")
                for a in alphas:
                    slot = a.get("slot_id")
                    status = a.get("status")
                    sharpe = a.get("sharpe")
                    fitness = a.get("fitness")
                    turnover = a.get("turnover")
                    formula = a.get("formula")
                    error_msg = a.get("error") or a.get("error_message") or ""
                    
                    total_active += 1
                    if status == "SIMULATING":
                        simulating_count += 1
                    elif status == "SUBMITTED":
                        passed_count += 1
                    elif status == "SOFT_FAIL":
                        soft_fail_count += 1
                    elif status in ("ERROR", "HARD_REJECT"):
                        failed_count += 1
                        
                    print(f"  Slot {slot} | Status: {status} | Sharpe: {sharpe} | Fit: {fitness} | Turn: {turnover}%")
                    print(f"    Formula: {formula}")
                    if error_msg:
                        print(f"    Error: {error_msg}")
                    print("-" * 50)
        except Exception as e:
            print(f"Error checking {group_name}: {e}")
            
    print("\n==========================================")
    print("CYCLE RESULTS SUMMARY:")
    print(f"  Total Alphas Checked: {total_active}")
    print(f"  Simulating: {simulating_count}")
    print(f"  Submitted (Pass): {passed_count}")
    print(f"  Soft Fail (Borderline): {soft_fail_count}")
    print(f"  Failed / Errored: {failed_count}")
    print("==========================================")

if __name__ == "__main__":
    main()

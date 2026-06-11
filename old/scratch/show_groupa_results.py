import urllib.request
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    url = "http://localhost:8000/api/status"
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer yashthakreop",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
            alphas = data.get("alphas", [])
            
            # Filter for slots 1-4
            group_a = [a for a in alphas if a.get("slot_id") in (1, 2, 3, 4)]
            print("==========================================")
            print(f"GROUP A ACTIVE SIMULATION RESULTS ({len(group_a)} total):")
            print("==========================================\n")
            
            statuses = {}
            for a in group_a:
                slot = a.get("slot_id")
                status = a.get("status")
                sharpe = a.get("sharpe")
                fitness = a.get("fitness")
                turnover = a.get("turnover")
                formula = a.get("formula")
                err_msg = a.get("error_message")
                
                statuses[status] = statuses.get(status, 0) + 1
                
                # Show simulating or successfully completed ones, and errors for debug
                if status in ("SIMULATING", "SUBMITTED", "SOFT_FAIL", "ERROR") or (sharpe is not None and float(sharpe) != 0.0):
                    print(f"Slot {slot} | Status: {status} | Sharpe: {sharpe} | Fit: {fitness} | Turn: {turnover}%")
                    print(f"  Formula: {formula[:100]}...")
                    if err_msg:
                        print(f"  Error: {err_msg}")
                    print("-" * 50)
            
            print("\nSTATUS SUMMARY:")
            for status, count in statuses.items():
                print(f"  {status}: {count}")
    except Exception as e:
        print(f"Error checking Group A: {e}")

if __name__ == "__main__":
    main()

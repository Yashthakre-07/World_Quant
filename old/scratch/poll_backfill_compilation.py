import requests
import json
import urllib3
import time

urllib3.disable_warnings()

url = "https://world-quant.onrender.com/api/status"

for i in range(12):  # Poll every 10 seconds for 2 minutes
    print(f"\nPolling iteration {i+1}/12 ...")
    try:
        r = requests.get(url, timeout=30, verify=False)
        if r.status_code == 200:
            data = r.json()
            alphas = data.get("alphas", [])
            print(f"Total alphas in queue: {len(alphas)}")
            
            completed = 0
            pending = 0
            running = 0
            failed = 0
            
            for a in alphas:
                formula = a.get("formula")
                status = a.get("status")
                progress = a.get("progress", 0)
                err = a.get("error_message")
                
                # Check if it's one of our test alphas
                if "backfill" in formula or "ts_corr" in formula:
                    print(f"- Formula: {formula[:100]}...")
                    print(f"  Status: {status} | Progress: {progress}% | Error: {err}")
                    
                    if status in ["SUBMITTED", "SUCCESS", "SOFT_FAIL", "HARD_REJECT"]:
                        completed += 1
                        if status == "HARD_REJECT" and err:
                            failed += 1
                    elif status == "RUNNING" or progress > 0:
                        running += 1
                    else:
                        pending += 1
            
            print(f"Summary: Completed={completed}, Running={running}, Pending={pending}")
            if completed == 5:
                print("All test alphas finished simulation!")
                break
        else:
            print(f"Failed to fetch status: {r.status_code}")
    except Exception as e:
        print(f"Error polling: {e}")
    time.sleep(10)

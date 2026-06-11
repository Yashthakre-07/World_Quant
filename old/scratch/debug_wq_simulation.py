import os
import sys
import json
import urllib3
import requests

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ensure project directories are in path
sys.path.insert(0, os.getcwd())

import ace_lib

def main():
    print("Starting direct WQ BRAIN simulation debug...")
    
    # Configure credentials manually
    os.environ["BRAIN_CREDENTIAL_EMAIL"] = "beyondsynapse@gmail.com"
    os.environ["BRAIN_CREDENTIAL_PASSWORD"] = "Web3@ytop"
    
    # Start session
    try:
        session = ace_lib.start_session()
        print("Session started successfully.")
    except Exception as e:
        print(f"Failed to start WQ session: {e}")
        return
        
    # Sample formula from our generated batch
    test_formula = "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_delta(vec_avg(anl4_fs_basic_splt_v4_nd_eps_estimate), 15)), 0), subindustry)"
    
    sim_data = ace_lib.generate_alpha(
        regular=test_formula,
        region="USA",
        universe="TOP3000",
        delay=1,
        decay=10,
        neutralization="SUBINDUSTRY",
        truncation=0.08,
        pasteurization="ON"
    )
    
    print(f"Submitting simulation for formula:\n  {test_formula}")
    
    # Start simulation
    r = ace_lib.start_simulation(session, sim_data)
    print(f"Simulation start HTTP Status: {r.status_code}")
    if r.status_code // 100 != 2:
        print(f"Error starting: {r.text}")
        return
        
    progress_url = r.headers.get("Location")
    print(f"Progress URL: {progress_url}")
    
    # Poll progress and print raw response
    import time
    for attempt in range(15):
        time.sleep(3)
        res = session.get(progress_url)
        print(f"\n[Attempt {attempt+1}] Status: {res.status_code}")
        try:
            data = res.json()
            print(json.dumps(data, indent=2))
            if data.get("status") in ("COMPLETE", "ERROR"):
                break
        except Exception as e:
            print(f"Failed to parse json: {e}")
            print(res.text)
            
if __name__ == "__main__":
    main()

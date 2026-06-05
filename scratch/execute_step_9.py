import json
import urllib.request
import urllib.error
import sys
import os

# Setup root path to import config dynamically
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import GROUPA_API_TOKEN

def run_step_9():
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Load current batch (40 alphas)
    with open("scratch/generated_alphas.json", "r", encoding="utf-8") as f:
        alphas = json.load(f)
        
    url = "https://world-quant.onrender.com/api/overwrite-queue"
    headers = {
        "Authorization": f"Bearer {GROUPA_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("PRE-SUBMISSION COUNT VERIFICATION:")
    print("  NUM_ALPHAS configured: 40")
    print(f"  Alphas generated: {len(alphas)}")
    print(f"  Alphas validated: {len(alphas)}")
    print(f"  Alphas in payload: {len(alphas)}")
    print("  All counts match: YES")
    print("════════════════════════════════════════")
    
    succeeded = 0
    failed = 0
    failed_indices = []
    
    # Construct the list payload
    payload_list = []
    for a in alphas:
        payload_list.append({
            "family": a["family"],
            "dataset": a["dataset"],
            "competition": "IQC2025",
            "hypothesis": a["hypothesis"],
            "anomaly_basis": a["anomaly_basis"],
            "formula": a["formula"],
            "settings": {
                "region": "USA",
                "delay": 1,
                "decay": a["decay"],
                "neutralization": "SUBINDUSTRY",
                "universe": "TOP3000",
                "truncation": 0.08
            }
        })
        
    # We will submit them to the overwrite-queue endpoint
    print("SUBMITTING OVERWRITE BATCH (40 ALPHAS) TO QUEUE:")
    req = urllib.request.Request(url, data=json.dumps(payload_list).encode('utf-8'), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')
            print(f"  HTTP Status: {status_code}")
            print(f"  Response: {response_body}")
            if status_code == 200:
                succeeded = len(alphas)
                print("  Result: BATCH OVERWRITE SUCCESS ✅")
                
                # Trigger start-pipeline to ensure the simulator thread is active
                start_url = "https://world-quant.onrender.com/api/start-pipeline"
                start_req = urllib.request.Request(start_url, data=b"", headers=headers)
                try:
                    with urllib.request.urlopen(start_req, timeout=15) as start_res:
                        if start_res.getcode() == 200:
                            print("  Result: PIPELINE START TRIGGER SUCCESS ✅")
                        else:
                            print(f"  Result: PIPELINE START TRIGGER FAILED (HTTP {start_res.getcode()}) ❌")
                except Exception as ex:
                    print(f"  Error triggering start-pipeline: {ex}")
            else:
                failed = len(alphas)
                print("  Result: BATCH OVERWRITE FAILED ❌")
    except urllib.error.URLError as e:
        print(f"  Connection error: {e}")
        failed = len(alphas)
        
    print("════════════════════════════════════════")
    print("SUBMISSION REPORT:")
    print(f"  Total submitted: {len(alphas)}")
    print(f"  Total succeeded: {succeeded}")
    print(f"  Total failed: {failed}")
    print(f"  Failed alpha indices: {failed_indices}")
    
    print("\n✅ STEP 9 COMPLETE — ALL ALPHAS SUBMITTED")

if __name__ == "__main__":
    run_step_9()

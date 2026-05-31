import requests
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URLS = {
    "Sai Profile": "https://world-quant.onrender.com/api/status",
    "Yash Profile": "https://world-quant-1.onrender.com/api/status"
}

for name, url in URLS.items():
    print(f"\n==========================================")
    print(f"ANALYZING FAILURES FOR: {name}")
    print(f"==========================================")
    try:
        r = requests.get(url, timeout=30, verify=False)
        if r.status_code == 200:
            data = r.json()
            alphas = data.get("alphas", [])
            print(f"Total alphas in queue: {len(alphas)}")
            
            # Group by status and summarize messages/errors
            by_status = {}
            for index, a in enumerate(alphas):
                st = a.get("status", "UNKNOWN")
                if st not in by_status:
                    by_status[st] = []
                by_status[st].append((index, a))
            
            for st, items in by_status.items():
                print(f"\nStatus: {st} ({len(items)} alphas)")
                # Print a few examples of errors/failures
                examples = items[:5]
                for idx, a in examples:
                    formula = a.get("formula", "")
                    err = a.get("error") or a.get("message") or a.get("failures")
                    sim_id = a.get("sim_id") or a.get("simulation_id")
                    print(f"  [{idx}] Formula: {formula[:80]}...")
                    print(f"      Sim ID: {sim_id}")
                    print(f"      Error/Message: {err}")
        else:
            print(f"Failed to fetch status: {r.status_code}")
    except Exception as e:
        print(f"Error checking: {e}")

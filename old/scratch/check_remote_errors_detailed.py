import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URLS = {
    "Sai Profile": "https://world-quant.onrender.com/api/status",
    "Yash Profile": "https://world-quant-1.onrender.com/api/status"
}

for name, url in URLS.items():
    print(f"\n==========================================")
    print(f"ERROR ANALYSIS FOR: {name}")
    print(f"==========================================")
    try:
        r = requests.get(url, timeout=30, verify=False)
        if r.status_code == 200:
            data = r.json()
            alphas = data.get("alphas", [])
            print(f"Total alphas in queue: {len(alphas)}")
            
            # Extract distinct error messages and statuses
            status_errors = {}
            for a in alphas:
                st = a.get("status")
                err = a.get("error_message")
                formula = a.get("formula")
                
                if st not in status_errors:
                    status_errors[st] = {}
                if err not in status_errors[st]:
                    status_errors[st][err] = []
                status_errors[st][err].append(formula)
            
            for st, err_dict in status_errors.items():
                print(f"\nStatus: {st} ({sum(len(v) for v in err_dict.values())} alphas)")
                for err, formulas in err_dict.items():
                    print(f"  - Error Message: {err}")
                    print(f"    Count: {len(formulas)}")
                    print(f"    Sample Formulas:")
                    for f in formulas[:3]:
                        print(f"      * {f}")
        else:
            print(f"Failed to fetch status: {r.status_code}")
    except Exception as e:
        print(f"Error checking: {e}")

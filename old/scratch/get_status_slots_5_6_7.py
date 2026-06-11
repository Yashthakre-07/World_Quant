import urllib.request
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check():
    servers = [
        "https://world-quant.onrender.com/api/status",
        "https://world-quant-1.onrender.com/api/status"
    ]
    tokens = ["yashthakrepro", "yashthakreop", "yashthakreop1"]
    
    for url in servers:
        for token in tokens:
            print(f"\n--- Checking URL: {url} | Token: {token} ---")
            req = urllib.request.Request(url, headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            })
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = json.loads(r.read().decode())
                    alphas = data.get("alphas", [])
                    print(f"Total alphas in pipeline: {len(alphas)}")
                    for idx, a in enumerate(alphas):
                        slot = a.get('slot_id')
                        status = a.get('status')
                        progress = a.get('progress')
                        sharpe = a.get('sharpe')
                        fitness = a.get('fitness')
                        turnover = a.get('turnover')
                        formula = a.get('formula')
                        err = a.get('error') or a.get('error_message') or a.get('errorMessage')
                        
                        print(f"[{idx+1}] Slot: {slot} | Status: {status} | Progress: {progress}% | Sharpe: {sharpe} | Fitness: {fitness} | Turnover: {turnover}")
                        print(f"    Formula: {formula}")
                        if err:
                            print(f"    Error: {err}")
            except Exception as e:
                print(f"Error fetching status: {e}")

if __name__ == "__main__":
    check()

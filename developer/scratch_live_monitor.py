import urllib.request, json, ssl, time
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url_status = 'https://world-quant.onrender.com/api/status'

def get_data(url):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def monitor():
    print("=" * 65)
    print("LIVE RUNNING PIPELINE MONITOR (VIA API/STATUS)")
    print("=" * 65)
    
    data = get_data(url_status)
    if not data:
        print("Failed to fetch status data.")
        return
        
    alphas = data.get('alphas', [])
    print(f"Pipeline Status: {data.get('status')}")
    print(f"Total Alphas in Queue: {len(alphas)}")
    
    # Analyze the statuses of the queue alphas
    status_counts = {}
    completed_runs = []
    running_runs = []
    pending_runs = []
    
    for a in alphas:
        stat = a.get('status', 'PENDING')
        status_counts[stat] = status_counts.get(stat, 0) + 1
        if stat in ('SUBMITTED', 'HARD_REJECT', 'SOFT_FAIL', 'ERROR'):
            completed_runs.append(a)
        elif stat in ('SIMULATING', 'RUNNING'):
            running_runs.append(a)
        else:
            pending_runs.append(a)
            
    print("\nQueue Status Breakdown:")
    for stat, count in status_counts.items():
        print(f"  {stat}: {count}")
        
    print(f"\nSimulating: {len(running_runs)} | Completed: {len(completed_runs)} | Pending: {len(pending_runs)}")
    
    if completed_runs:
        print("\n=== COMPLETED ALPHAS ===")
        # Sort by status (SUBMITTED first, then SOFT_FAIL)
        completed_runs.sort(key=lambda x: (x.get('status') != 'SUBMITTED', -(x.get('fitness') or 0)))
        for a in completed_runs:
            print(f"  [{a.get('status')}] F={a.get('fitness')} S={a.get('sharpe')} TO={a.get('turnover')}%")
            print(f"    Family: {a.get('family')}")
            print(f"    Formula: {a.get('formula')[:80]}...")
            if a.get('error_message'):
                print(f"    Error: {a.get('error_message')}")
            print("-" * 50)
            
    if running_runs:
        print("\n=== RUNNING NOW ===")
        for a in running_runs:
            print(f"  [{a.get('status')} - {a.get('progress')}%] {a.get('family')}")
            print(f"    Formula: {a.get('formula')[:80]}...")
            print("-" * 50)

    # Print logs
    logs = data.get('logs', [])
    if logs:
        print("\n=== LATEST LOGS ===")
        for l in logs[-15:]:
            print(f"  {l}")

if __name__ == "__main__":
    monitor()

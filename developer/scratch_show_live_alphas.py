import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://world-quant.onrender.com/api/status'
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        alphas = data.get('alphas', [])
        print(f"=== LIVE PIPELINE ALPHAS STATUS (Total: {len(alphas)}) ===")
        
        status_counts = {}
        for a in alphas:
            status = a.get('status', 'PENDING')
            status_counts[status] = status_counts.get(status, 0) + 1
            
        print("Status Counts:")
        for s, count in status_counts.items():
            print(f"  {s}: {count}")
            
        print("\n=== DETAILED STATUS (NEWEST FIRST) ===")
        for idx, a in enumerate(alphas):
            formula = a.get('formula', '')
            status = a.get('status', 'PENDING')
            progress = a.get('progress', 0)
            sharpe = a.get('sharpe')
            fitness = a.get('fitness')
            turnover = a.get('turnover')
            err = a.get('error_message')
            print(f"#{idx+1} | {status} ({progress}%) | Sharpe: {sharpe} | Fitness: {fitness} | Turnover: {turnover}%")
            print(f"  Family: {a.get('family')}")
            print(f"  Formula: {formula[:100]}...")
            if err:
                print(f"  Error: {err}")
            print("-" * 80)
            
except Exception as e:
    print(e)

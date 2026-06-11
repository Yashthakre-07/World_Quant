import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://world-quant.onrender.com/api/stats'
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        vault_alphas = data.get('vault_alphas', [])
        print(f"Total vault alphas on server: {len(vault_alphas)}")
        
        # Sort by creation time / alpha_id to see the newest ones first
        # We can also filter for any run on 2026-05-23
        runs_today = [a for a in vault_alphas if "2026-05-23" in a.get('created_at', '')]
        print(f"Total simulated/running today: {len(runs_today)}")
        
        # Print status
        print("\n=== STATUS BREAKDOWN FOR TODAY ===")
        status_counts = {}
        for a in runs_today:
            status_counts[a['status']] = status_counts.get(a['status'], 0) + 1
        for s, count in status_counts.items():
            print(f"{s}: {count}")
            
        print("\n=== DETAILS OF NEW RUNS TODAY ===")
        runs_today.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        for a in runs_today:
            f = a.get('fitness')
            s = a.get('sharpe')
            t = a.get('turnover')
            status = a.get('status')
            created = a.get('created_at')
            formula = a.get('formula', '')
            err = a.get('error_message', '')
            print(f"Created: {created} | S={s} F={f} TO={t} | {status}")
            print(f"  Formula: {formula[:100]}...")
            if err:
                print(f"  Error: {err}")
            print("-" * 80)
            
except Exception as e:
    print(e)

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
        print("\n=== DETAILS OF ALL RUNS (NEWEST FIRST) ===")
        # Sort desc
        for idx, a in enumerate(vault_alphas[:50]):
            f = a.get('fitness')
            s = a.get('sharpe')
            t = a.get('turnover')
            status = a.get('status')
            created = a.get('created_at')
            formula = a.get('formula', '')
            err = a.get('error_message', '')
            print(f"#{idx+1} | S={s} F={f} TO={t}% | {status} | Created: {created}")
            print(f"  Formula: {formula[:120]}...")
            if err:
                print(f"  Error: {err}")
            print("-" * 80)
            
except Exception as e:
    print(e)

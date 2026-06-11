import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://world-quant.onrender.com/api/stats'
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        
        print('\n[ TOP PERFORMING ALPHAS (Fitness > 1.0) ]')
        print('-'*80)
        submitted = [a for a in data.get('recent_alphas', []) if a.get('fitness', 0) > 1.0]
        submitted.sort(key=lambda x: x.get('fitness', 0), reverse=True)
        
        for a in submitted:
            f_str = f"{a.get('fitness', 0):.2f}"
            s_str = f"{a.get('sharpe', 0):.2f}"
            t_str = f"{a.get('turnover', 0):.2f}%"
            print(f"Fitness: {f_str} | Sharpe: {s_str} | Turnover: {t_str} | Status: {a.get('status')}")
            print(f"  Formula: {a.get('formula')[:120]}...")
            print('-'*80)
            
        print(f"\nTotal in history: {len(data.get('recent_alphas', []))}")
except Exception as e:
    print(f'Error: {e}')

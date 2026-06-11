import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://world-quant.onrender.com/api/alphas'
TOKEN = 'yashthakreop'
try:
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        alphas = data.get('alphas', [])
        print(f"Total alphas on server: {len(alphas)}")
        alphas.sort(key=lambda x: (x.get('fitness') or 0), reverse=True)
        for a in alphas:
            f = a.get('fitness')
            s = a.get('sharpe')
            t = a.get('turnover')
            status = a.get('status')
            formula = a.get('formula', '')
            print(f"ID={a.get('alpha_id')} | S={s} F={f} TO={t} | {status} | {formula[:85]}")
except Exception as e:
    print(e)

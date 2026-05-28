import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://world-quant.onrender.com/api/status'
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        logs = data.get('logs', [])
        print("=== LIVE SERVER LOGS ===")
        for log in logs[-80:]:
            print(log)
            
except Exception as e:
    print(e)

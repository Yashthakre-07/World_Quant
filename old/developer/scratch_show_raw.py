import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(ep):
    url = f'https://world-quant.onrender.com{ep}'
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"--- {ep} ---")
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(e)

fetch('/api/queue-status')
fetch('/api/status')

import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://world-quant.onrender.com/api/status'
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"Pipeline Active: {data.get('pipeline_active')}")
        print(f"Alphas in Queue: {data.get('queue_size')}")
        print(f"Active Threads: {data.get('active_threads')}")
        print(f"Total Processed: {data.get('processed_count')}")
        print(f"Stats: {data.get('stats')}")
except Exception as e:
    print(e)

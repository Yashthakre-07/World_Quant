import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://world-quant.onrender.com/api/queue-status'
try:
    with urllib.request.urlopen(url, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"Queue Size on disk: {data.get('queue_on_disk')}")
        print(f"In memory size: {data.get('in_memory')}")
        print(f"Pipeline Status: {data.get('pipeline_status')}")
        print("Formulas in queue:")
        for f in data.get('formulas', []):
            print(f"  {f}")
except Exception as e:
    print(e)

import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
req = urllib.request.Request('https://world-quant.onrender.com/api/status')
try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        print('=====================================')
        print('PIPELINE STATUS REPORT')
        print('=====================================')
        print(f"Pipeline Active: {data.get('pipeline_active')}")
        print(f"Alphas in Queue: {data.get('queue_size')}")
        print(f"Active Threads:  {data.get('active_threads')}")
        print(f"Total Processed: {data.get('processed_count')}")
        print('-------------------------------------')
        stats = data.get('stats', {})
        print(f"SUBMITTED:    {stats.get('SUBMITTED', 0)}")
        print(f"SOFT_FAIL:    {stats.get('SOFT_FAIL', 0)}")
        print(f"HARD_REJECT:  {stats.get('HARD_REJECT', 0)}")
        print(f"ERROR:        {stats.get('ERROR', 0)}")
        print('=====================================')
except Exception as e:
    print(f'Error fetching report: {e}')

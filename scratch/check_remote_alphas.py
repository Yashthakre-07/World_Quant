import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URLS = {
    "world-quant (Sai Profile)": {
        "url": "https://world-quant.onrender.com/api/status",
        "token": "yashthakreop"
    },
    "world-quant-1 (Yash Profile)": {
        "url": "https://world-quant-1.onrender.com/api/status",
        "token": "yashthakreop1"
    }
}

for name, info in URLS.items():
    print(f"DIAGNOSING ALPHAS ON: {name}")
    headers = {
        "Authorization": f"Bearer {info['token']}"
    }
    try:
        r = requests.get(info["url"], headers=headers, timeout=40, verify=False)
        if r.status_code == 200:
            data = r.json()
            alphas = data.get("alphas", [])
            print(f"Total Alphas in Queue: {len(alphas)}")
            
            # Count statuses
            status_counts = {}
            for a in alphas:
                st = a.get("status", "UNKNOWN")
                status_counts[st] = status_counts.get(st, 0) + 1
            
            print(f"Status breakdown: {status_counts}")
            if alphas:
                print(f"Sample Alpha 1: {alphas[0].get('formula', '')[:60]}... | Status: {alphas[0].get('status')}")
        else:
            print(f"[FAILED] Status code {r.status_code}: {r.text[:300]}")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
    print("=" * 60)

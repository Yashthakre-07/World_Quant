import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SERVERS = {
    "world-quant (Sai)": "https://world-quant.onrender.com",
    "world-quant-1 (Yash)": "https://world-quant-1.onrender.com"
}

for name, url in SERVERS.items():
    print(f"\nQuerying stats for {name}...")
    try:
        req = urllib.request.Request(f"{url}/api/stats", method="GET")
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            vault = data.get("vault_alphas", [])
            print(f"  Total vault_alphas: {len(vault)}")
            print(f"  Total runs: {data.get('total_runs')}")
            print(f"  Total submissions: {data.get('total_submissions')}")
    except Exception as e:
        print(f"  FAILED: {e}")

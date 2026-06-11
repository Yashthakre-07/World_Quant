import urllib.request
import json
import ssl
import sys

# Disable SSL verification issues if any
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SERVERS = {
    "Sai's Server (world-quant)": {
        "url": "https://world-quant.onrender.com",
        "token": "yashthakreop"
    },
    "Yash's Server (world-quant-1)": {
        "url": "https://world-quant-1.onrender.com",
        "token": "yashthakreop1"
    }
}

def query_endpoint(server_url, path, token, requires_auth=False):
    url = f"{server_url.rstrip('/')}{path}"
    req = urllib.request.Request(url, method="GET")
    if requires_auth:
        req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body), response.status
    except Exception as e:
        return {"error": str(e)}, 500

def main():
    results = {}
    for name, config in SERVERS.items():
        print(f"\n==========================================")
        print(f"QUERYING: {name}")
        print(f"URL: {config['url']}")
        print(f"==========================================")
        
        # 1. Query /api/session
        session_data, _ = query_endpoint(config['url'], "/api/session", config['token'])
        print(f"Session info fetched.")
        
        # 2. Query /api/status
        status_data, _ = query_endpoint(config['url'], "/api/status", config['token'])
        print(f"Status info fetched. Alphas in queue: {len(status_data.get('alphas', []))}")
        
        # 3. Query /api/stats
        stats_data, _ = query_endpoint(config['url'], "/api/stats", config['token'])
        print(f"Stats fetched.")
        
        # 4. Query /api/alphas
        alphas_data, _ = query_endpoint(config['url'], "/api/alphas", config['token'], requires_auth=True)
        num_alphas = len(alphas_data.get('alphas', [])) if isinstance(alphas_data, dict) else 0
        print(f"Alphas fetched. Successful alphas on disk: {num_alphas}")
        
        results[name] = {
            "session": session_data,
            "status": status_data,
            "stats": stats_data,
            "alphas": alphas_data
        }
        
    with open("both_servers_report.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\nSuccessfully queried both servers and saved report to both_servers_report.json")

if __name__ == "__main__":
    main()

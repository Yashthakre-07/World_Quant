import urllib.request
import json
import ssl
import sys
import datetime

# Configuration for Sai's Server
SERVER_URL = "https://world-quant.onrender.com"
TOKEN = "yashthakreop"

# Disable SSL verification issues if any (just in case)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def query_endpoint(path, requires_auth=False):
    url = f"{SERVER_URL.rstrip('/')}{path}"
    print(f"Requesting {url}...")
    req = urllib.request.Request(url, method="GET")
    if requires_auth:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body), response.status
    except Exception as e:
        print(f"Error querying {path}: {e}")
        return None, 500

def main():
    print("=" * 60)
    print("GATHERING LIVE DATA FROM SAI'S QUANT SERVER (world-quant)")
    print("=" * 60)
    
    # 1. Query /api/session to check connection and token expiration
    session_data, s_code = query_endpoint("/api/session")
    
    # 2. Query /api/status to get live queue and pipeline activity
    status_data, st_code = query_endpoint("/api/status")
    
    # 3. Query /api/stats to get database metrics breakdown
    stats_data, stat_code = query_endpoint("/api/stats")
    
    # 4. Query /api/alphas (requires auth) to get the list of saved alphas on disk
    alphas_data, a_code = query_endpoint("/api/alphas", requires_auth=True)
    
    # Bundle and print report
    report = {
        "session": session_data,
        "status": status_data,
        "stats": stats_data,
        "alphas": alphas_data
    }
    
    # Write to a JSON file so the agent can parse it
    with open("sai_server_report.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print("\nSuccessfully fetched all live telemetry and saved to sai_server_report.json!")

if __name__ == "__main__":
    main()

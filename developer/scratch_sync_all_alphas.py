import os
import json
import urllib.request
import urllib.error
import ssl
from pathlib import Path

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

def make_request(server_url, token, path, method="GET", data=None):
    url = f"{server_url.rstrip('/')}{path}"
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode("utf-8")
        
    req = urllib.request.Request(url, data=req_data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body), response.status
    except Exception as e:
        return {"error": str(e)}, 500

def main():
    local_dir = Path(__file__).resolve().parent / "alphas"
    local_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("STARTING DUAL-SERVER ALPHA HARVESTER & SYNCHRONIZER")
    print("=" * 60)
    print(f"Local storage directory: {local_dir.resolve()}\n")
    
    total_synced = 0
    total_skipped = 0
    
    for name, config in SERVERS.items():
        print(f"\nScanning {name}...")
        res, status = make_request(config["url"], config["token"], "/api/alphas")
        
        if status != 200:
            print(f"  [ERROR] Failed to fetch list (HTTP {status}): {res.get('error')}")
            continue
            
        remote_alphas = res.get("alphas", [])
        print(f"  Found {len(remote_alphas)} simulated alphas on remote storage.")
        
        server_synced = 0
        server_skipped = 0
        
        for ra in remote_alphas:
            alpha_id = ra.get("alpha_id")
            if not alpha_id:
                continue
                
            filename = f"alpha_{alpha_id}.json"
            local_file = local_dir / filename
            
            # If the file is not present locally, download it directly from that server
            if not local_file.exists():
                print(f"    [SYNC] Downloading {filename}...")
                alpha_data, a_status = make_request(config["url"], config["token"], f"/api/alpha/{alpha_id}")
                if a_status == 200:
                    with open(local_file, "w") as lf:
                        json.dump(alpha_data, lf, indent=2)
                    print(f"      [OK] Saved successfully.")
                    server_synced += 1
                else:
                    print(f"      [ERROR] Download failed: {alpha_data.get('error')}")
            else:
                server_skipped += 1
                
        print(f"  {name} Sync Complete: {server_synced} downloaded, {server_skipped} already existed.")
        total_synced += server_synced
        total_skipped += server_skipped
        
    print("\n" + "=" * 60)
    print("* TOTAL HARVEST RESULTS *")
    print("=" * 60)
    print(f"Total New Alphas Synced: {total_synced}")
    print(f"Total Alphas Skipped (Already Local): {total_skipped}")
    print(f"Total Alphas in Local Repository: {len(list(local_dir.glob('alpha_*.json')))}")
    print("=" * 60)

if __name__ == "__main__":
    main()

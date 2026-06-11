import urllib.request
import json
import ssl

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

def query_endpoint(server_url, path, token, method="GET", data=None, requires_auth=False):
    url = f"{server_url.rstrip('/')}{path}"
    
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode("utf-8")
        
    req = urllib.request.Request(url, method=method, data=req_data)
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
    for name, config in SERVERS.items():
        print(f"\n==========================================")
        print(f"CHECKING INBOX FOR: {name}")
        print(f"==========================================")
        
        # Query inbox
        inbox_alphas, code = query_endpoint(config['url'], "/api/inbox-alphas", config['token'])
        if code != 200 or isinstance(inbox_alphas, dict) and "error" in inbox_alphas:
            print(f"Error querying inbox: {inbox_alphas}")
            continue
            
        print(f"Total alphas in inbox: {len(inbox_alphas)}")
        for idx, a in enumerate(inbox_alphas):
            print(f"  [{idx+1}] {a.get('family', 'No Family')} | {a.get('formula')[:80]}...")
            
        if len(inbox_alphas) > 0:
            print(f"Injecting inbox alphas to simulation queue...")
            inject_res, code = query_endpoint(
                config['url'], 
                "/api/inject-inbox", 
                config['token'], 
                method="POST", 
                data={"all": True}
            )
            print(f"Injection status code: {code} | Response: {inject_res}")
        else:
            print("Inbox is empty, no injection needed.")

if __name__ == "__main__":
    main()

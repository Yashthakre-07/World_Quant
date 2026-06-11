import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://world-quant-1.onrender.com/api/alphas"
token = "yashthakreop1"

print(f"Connecting to Yash's server (world-quant-1) with 180s timeout...")
req = urllib.request.Request(url, method="GET")
req.add_header("Authorization", f"Bearer {token}")
req.add_header("Content-Type", "application/json")

try:
    with urllib.request.urlopen(req, context=ctx, timeout=180) as response:
        res_body = response.read().decode("utf-8")
        data = json.loads(res_body)
        alphas = data.get("alphas", [])
        print(f"SUCCESS! Status Code: {response.status}")
        print(f"Total alphas in Yash's Vault: {len(alphas)}")
        
        # Save to local file
        with open("yash_vault_alphas.json", "w") as f:
            json.dump(data, f, indent=2)
        print("Saved to yash_vault_alphas.json")
except Exception as e:
    print(f"FAILED: {e}")

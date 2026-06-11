import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Let's check Sai's Server for the first disk alpha we found: e7LpREVd
server_url = "https://world-quant.onrender.com"
token = "yashthakreop"
alpha_id = "e7LpREVd"

url = f"{server_url}/api/alpha/{alpha_id}"
req = urllib.request.Request(url)
req.add_header("Authorization", f"Bearer {token}")
req.add_header("Content-Type", "application/json")

try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Alpha details from server:")
        print(json.dumps(data, indent=2))
except Exception as e:
    print("Error:", e)

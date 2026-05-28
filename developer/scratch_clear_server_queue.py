import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://world-quant.onrender.com/api/clear-queue"
token = "yashthakreop"

req = urllib.request.Request(url, method="POST")
req.add_header("Authorization", f"Bearer {token}")
req.add_header("Content-Type", "application/json")

print(f"Connecting to clear queue: {url}...")
try:
    with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
        res_body = response.read().decode("utf-8")
        print(f"SUCCESS! Status Code: {response.status}")
        print(f"Server Response: {res_body}")
except Exception as e:
    print(f"FAILED: {e}")

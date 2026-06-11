import urllib.request
import json

url = "http://localhost:8000/api/status"
req = urllib.request.Request(url, headers={
    "Authorization": "Bearer yashthakreop",
    "Content-Type": "application/json"
})
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read().decode())
        print("Pipeline State keys:")
        for k, v in data.items():
            if k != "alphas":
                print(f"  {k}: {v}")
            else:
                print(f"  alphas count: {len(v)}")
except Exception as e:
    print(f"Error: {e}")

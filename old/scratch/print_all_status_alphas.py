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
        alphas = data.get("alphas", [])
        print(f"Total alphas in response: {len(alphas)}")
        for idx, a in enumerate(alphas):
            print(f"[{idx+1}] Slot: {a.get('slot_id')} | Status: {a.get('status')} | Progress: {a.get('progress')}% | Sharpe: {a.get('sharpe')}")
            print(f"    Formula: {a.get('formula')[:100]}...")
except Exception as e:
    print(f"Error: {e}")

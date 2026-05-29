import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://world-quant.onrender.com/api/status"
print(f"Connecting to: {url} ...")
try:
    r = requests.get(url, timeout=30, verify=False)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        logs = data.get("logs", [])
        print(f"Total log lines received: {len(logs)}")
        print("\n=== LAST 60 REMOTE LOG LINES (SAFE ENCODING) ===")
        for line in logs[-60:]:
            # Encode to ASCII, ignoring non-ASCII characters, then decode back to string
            safe_line = line.encode('ascii', errors='ignore').decode('ascii')
            print(safe_line)
    else:
        print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Failed to fetch logs: {e}")

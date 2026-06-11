import urllib.request
import json

SERVERS = [
    ("Sai (world-quant)", "https://world-quant.onrender.com", "yashthakreop"),
    ("Yash (world-quant-1)", "https://world-quant-1.onrender.com", "yashthakrepro"),
]

for name, base, token in SERVERS:
    print(f"\n=== {name} ===")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 1. Check session
    try:
        req = urllib.request.Request(base + "/api/session", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            expired = data.get("expired")
            remaining = data.get("remaining_seconds")
            print(f"  Session expired={expired}, remaining={remaining}s")
    except Exception as e:
        print(f"  Session check ERROR: {e}")

    # 2. Force reauthenticate
    try:
        req = urllib.request.Request(
            base + "/api/reauthenticate",
            data=b"{}",
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read().decode()
            print(f"  Reauth HTTP {r.status}: {body[:300]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  Reauth HTTP {e.code}: {body[:300]}")
    except Exception as e:
        print(f"  Reauth ERROR: {e}")

print("\nDone.")

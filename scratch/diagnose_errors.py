import requests
import urllib3
import json
from collections import Counter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SERVERS = {
    "world-quant (Sai Profile)": {
        "url": "https://world-quant.onrender.com/api/status",
        "token": "yashthakreop"
    },
    "world-quant-1 (Yash Profile)": {
        "url": "https://world-quant-1.onrender.com/api/status",
        "token": "yashthakreop1"
    }
}

for name, info in SERVERS.items():
    print("=" * 70)
    print(f"SERVER: {name}")
    print("=" * 70)
    headers = {"Authorization": f"Bearer {info['token']}"}
    try:
        r = requests.get(info["url"], headers=headers, timeout=30, verify=False)
        if r.status_code != 200:
            print(f"[FAIL] Status {r.status_code}: {r.text[:200]}")
            continue
        data = r.json()
        alphas = data.get("alphas", [])
        
        # Group by status
        status_counts = Counter(a.get("status") for a in alphas)
        print(f"\nTotal alphas in pipeline: {len(alphas)}")
        print("Status breakdown:")
        for st, cnt in sorted(status_counts.items(), key=lambda x: -x[1]):
            print(f"  {st}: {cnt}")
        
        # Extract all errors
        errors = [a for a in alphas if a.get("status") in ("ERROR", "HARD_REJECT")]
        print(f"\nTotal errors/rejects: {len(errors)}")
        
        # Group errors by error message
        err_msgs = Counter()
        for a in errors:
            msg = a.get("message") or a.get("error") or a.get("result") or "No message"
            # Shorten to first 120 chars for grouping
            key = str(msg)[:120]
            err_msgs[key] += 1
        
        print("\nError message groups:")
        for msg, cnt in err_msgs.most_common(20):
            print(f"  [{cnt}x] {msg}")
        
        # Show 5 full error samples
        print("\n--- 5 Sample Error Alpha Details ---")
        for a in errors[:5]:
            print(f"  Name:    {a.get('name', 'N/A')}")
            print(f"  Status:  {a.get('status', 'N/A')}")
            print(f"  Formula: {a.get('formula', a.get('regular', 'N/A'))[:100]}")
            print(f"  Message: {a.get('message', a.get('error', a.get('result', 'N/A')))}")
            print()
    except Exception as e:
        print(f"[ERROR] {e}")
    print()

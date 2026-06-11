"""
Full error breakdown — categorize ALL error messages across entire pipeline.
"""
import requests
import urllib3
from collections import Counter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SERVERS = {
    "world-quant (Sai Profile)": {
        "status_url": "https://world-quant.onrender.com/api/status",
        "token": "yashthakreop"
    },
    "world-quant-1 (Yash Profile)": {
        "status_url": "https://world-quant-1.onrender.com/api/status",
        "token": "yashthakreop1"
    }
}

for name, info in SERVERS.items():
    print("=" * 70)
    print(f"SERVER: {name}")
    print("=" * 70)
    headers = {"Authorization": f"Bearer {info['token']}"}
    r = requests.get(info["status_url"], headers=headers, timeout=30, verify=False)
    data = r.json()
    alphas = data.get("alphas", [])

    status_counts = Counter(a.get("status") for a in alphas)
    print(f"\nTotal alphas: {len(alphas)}")
    for s, c in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"  {s}: {c}")

    errors = [a for a in alphas if a.get("status") in ("ERROR", "HARD_REJECT")]
    
    # Group by clean error message
    err_msg_counts = Counter()
    for a in errors:
        msg = a.get("error_message") or "No message"
        # Normalize: strip HTML tags
        import re
        msg_clean = re.sub(r'<[^>]+>', '', msg).strip()
        err_msg_counts[msg_clean] += 1

    print(f"\nUnique error types ({len(err_msg_counts)} groups):")
    for msg, cnt in err_msg_counts.most_common(30):
        print(f"\n  [{cnt}x] >>> {msg}")

    # Show 1 sample formula per unique error
    print("\n--- 1 Sample Formula Per Error Type ---")
    seen_msgs = set()
    for a in errors:
        msg = a.get("error_message") or "No message"
        msg_clean = re.sub(r'<[^>]+>', '', msg).strip()
        if msg_clean not in seen_msgs:
            seen_msgs.add(msg_clean)
            print(f"\nError:   {msg_clean}")
            print(f"Formula: {a.get('formula', '')[:150]}")
    print()

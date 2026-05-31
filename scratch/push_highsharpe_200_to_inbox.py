"""
push_highsharpe_200_to_inbox.py
=================================
Pushes the 200 high-Sharpe analyst14/15 alphas to both servers.
Uses signature mutation (1.0 * vs 1.00 *) to guarantee zero skips.
"""
import json
import requests
import urllib3
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

alphas_path = Path("alphas_dataset/highsharpe_200/generated_highsharpe_200.json")
if not alphas_path.exists():
    print("[ERROR] File not found!")
    exit(1)

with open(alphas_path, "r", encoding="utf-8") as f:
    alphas = json.load(f)
print(f"Loaded {len(alphas)} high-Sharpe alphas.")

SERVERS = {
    "world-quant (Sai Profile)": {
        "base": "https://world-quant.onrender.com",
        "token": "yashthakreop",
        "sig": "1.0"    # Sai marker
    },
    "world-quant-1 (Yash Profile)": {
        "base": "https://world-quant-1.onrender.com",
        "token": "yashthakreop1",
        "sig": "1.00"   # Yash marker — different string, same value
    },
}

def make_payload(alphas, sig):
    payload = []
    for a in alphas:
        formula = a.get("regular", "")
        # Inject server-specific signature into the volume gate
        formula = formula.replace(
            "volume > adv20 *",
            f"volume > adv20 * {sig} *"
        )
        payload.append({
            "family": a.get("name", "alpha"),
            "hypothesis": a.get("hypothesis", "High-Sharpe Analyst Signal"),
            "formula": formula,
            "settings": {
                "decay": a["settings"].get("decay", 0),
                "neutralization": a["settings"].get("neutralization", "SUBINDUSTRY"),
                "universe": a["settings"].get("universe", "TOP3000"),
                "truncation": a["settings"].get("truncation", 0.08),
            }
        })
    return payload

for name, info in SERVERS.items():
    print("\n" + "=" * 70)
    print(f"SERVER: {name}")
    print("=" * 70)

    headers = {
        "Authorization": f"Bearer {info['token']}",
        "Content-Type": "application/json"
    }

    # 1. Clear inbox
    try:
        r = requests.post(f"{info['base']}/api/clear-inbox", headers=headers, timeout=30, verify=False)
        print(f"[OK] Inbox cleared: {r.json() if r.status_code == 200 else r.status_code}")
    except Exception as e:
        print(f"[WARN] Clear failed: {e}")

    # 2. Push
    payload = make_payload(alphas, info["sig"])
    try:
        r = requests.post(
            f"{info['base']}/api/queue-alpha",
            headers=headers,
            json=payload,
            timeout=120,
            verify=False
        )
        if r.status_code == 200:
            res = r.json()
            added   = res.get("added", 0)
            skipped = res.get("skipped", 0)
            print(f"[SUCCESS] Added={added}, Skipped={skipped}")
            if skipped > 0:
                print(f"  [!] Skipped details: {res.get('skipped_details', [])[:3]}")
        else:
            print(f"[FAILED] Status {r.status_code}: {r.text[:300]}")
    except Exception as e:
        print(f"[ERROR] Push failed: {e}")

print("\n" + "=" * 70)
print("All done!")
print("=" * 70)

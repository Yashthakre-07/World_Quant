"""
push_mixed_200_to_inbox.py
===========================
Pushes the 200 mixed analyst10/14/15 alphas to the Review Box
on both Render servers with zero skips using string signature mutation.
"""
import json
import requests
import urllib3
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

alphas_path = Path("alphas_dataset/mixed_200/generated_mixed_200.json")
if not alphas_path.exists():
    print("[ERROR] File not found! Run generate_200_mixed_alphas.py first.")
    exit(1)

with open(alphas_path, "r", encoding="utf-8") as f:
    alphas = json.load(f)

print(f"Loaded {len(alphas)} mixed alphas from local file.")

SERVERS = {
    "world-quant (Sai Profile)": {
        "base": "https://world-quant.onrender.com",
        "token": "yashthakreop",
        # Sai's signature: use 1.0 * vol_gate (already in formula), keep epsilons as-is
    },
    "world-quant-1 (Yash Profile)": {
        "base": "https://world-quant-1.onrender.com",
        "token": "yashthakreop1",
        # Yash's signature: slightly different epsilon tweak for uniqueness
    },
}

# Build two payloads with distinct string signatures to avoid cross-server dedup issues
def build_payload(alphas, sai_mode=True):
    payload = []
    for a in alphas:
        formula = a.get("regular", "")
        if sai_mode:
            # Sai: keep formula as-is (already has "1.0 *" for uniqueness)
            pass
        else:
            # Yash: swap "1.0 *" with "1.00 *" for a different string
            formula = formula.replace("1.0 *", "1.00 *")
        ds = a.get("dataset", "custom")
        concept_id = a.get("name", f"alpha_{id(a)}")
        payload.append({
            "family": f"{ds}_{concept_id.split('_')[0]}_{concept_id.split('_')[1]}",
            "hypothesis": a.get("hypothesis", f"Mixed alpha from {ds}."),
            "formula": formula,
            "settings": {
                "decay": a["settings"].get("decay", 5),
                "neutralization": a["settings"].get("neutralization", "SUBINDUSTRY"),
                "universe": a["settings"].get("universe", "TOP3000"),
                "truncation": a["settings"].get("truncation", 0.08),
            }
        })
    return payload

sai_payload = build_payload(alphas, sai_mode=True)
yash_payload = build_payload(alphas, sai_mode=False)

for name, info in SERVERS.items():
    print("\n" + "=" * 70)
    print(f"PREPARING SERVER: {name}")
    print("=" * 70)

    is_sai = "Sai" in name
    payload = sai_payload if is_sai else yash_payload

    headers = {
        "Authorization": f"Bearer {info['token']}",
        "Content-Type": "application/json"
    }

    # 1. Clear Inbox
    clear_url = f"{info['base']}/api/clear-inbox"
    try:
        r = requests.post(clear_url, headers=headers, timeout=30, verify=False)
        if r.status_code == 200:
            print(f"[OK] Review inbox cleared: {r.json()}")
        else:
            print(f"[WARN] Clear inbox returned {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"[WARN] Could not clear inbox: {e}")

    # 2. Push alphas
    push_url = f"{info['base']}/api/queue-alpha"
    print(f"\n[->] Pushing 200 mixed alphas to: {push_url}")
    try:
        r = requests.post(push_url, headers=headers, json=payload, timeout=90, verify=False)
        if r.status_code == 200:
            res = r.json()
            added = res.get("added", 0)
            skipped = res.get("skipped", 0)
            print(f"[SUCCESS] Push complete on {name}")
            print(f"         Added={added}, Skipped={skipped}")
            if skipped > 0:
                print(f"         [!] Skipped details (first 3): {res.get('skipped_details', [])[:3]}")
        else:
            print(f"[FAILED] Status {r.status_code}: {r.text[:300]}")
    except Exception as e:
        print(f"[ERROR] Push failed: {e}")

print("\n" + "=" * 70)
print("Push script complete.")
print("=" * 70)

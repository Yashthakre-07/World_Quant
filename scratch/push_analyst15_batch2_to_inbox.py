import json
import requests
import urllib3
from pathlib import Path
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load the 100 newly generated analyst15 Batch 2 alphas
alphas_path = Path("alphas_dataset/analyst15/alphas/generated_alphas_200.json")
if not alphas_path.exists():
    print("[ERROR] Generated Batch 2 alphas file not found!")
    exit(1)

with open(alphas_path, "r", encoding="utf-8") as f:
    alphas = json.load(f)

print(f"Loaded {len(alphas)} analyst15 Batch 2 alphas from local file.")

# Format payload for /api/queue-alpha
push_payload = []
for idx, a in enumerate(alphas, 1):
    push_payload.append({
        "family": a.get("family", f"analyst15_batch2_concept_{a['name'].split('_')[2]}"),
        "hypothesis": a.get("hypothesis", "Premium Earnings Forecasts alpha (Batch 2)."),
        "formula": a.get("regular"),
        "settings": {
            "decay": a["settings"].get("decay", 5),
            "neutralization": a["settings"].get("neutralization", "SUBINDUSTRY"),
            "universe": a["settings"].get("universe", "TOP3000"),
            "truncation": a["settings"].get("truncation", 0.08)
        }
    })

print(f"Prepared payload with {len(push_payload)} alphas.")

URLS = {
    "world-quant (Sai Profile)": {
        "url": "https://world-quant.onrender.com/api/queue-alpha",
        "token": "yashthakreop"
    },
    "world-quant-1 (Yash Profile)": {
        "url": "https://world-quant-1.onrender.com/api/queue-alpha",
        "token": "yashthakreop1"
    }
}

for name, info in URLS.items():
    print("=" * 70)
    print(f"PUSHING BATCH 2 ALPHAS TO REVIEW BOX ON: {name}")
    print("=" * 70)
    
    headers = {
        "Authorization": f"Bearer {info['token']}",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.post(info["url"], headers=headers, json=push_payload, timeout=60, verify=False)
        if r.status_code == 200:
            res_data = r.json()
            print(f"[SUCCESS] Batch 2 alphas successfully pushed to review box on {name}.")
            print(f"Server Response: Added={res_data.get('added', 0)}, Skipped={res_data.get('skipped', 0)}")
        else:
            print(f"[FAILED] Server {name} returned status code {r.status_code}")
            print(f"Server Response: {r.text[:500]}")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
    print("\n" + "=" * 70 + "\n")

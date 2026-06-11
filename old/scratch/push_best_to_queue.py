import sqlite3
import urllib.request
import json
import sys

DB_PATH = "db/alpha_vault.db"
URL = "https://world-quant.onrender.com/api/queue-alpha"
HEADERS = {
    "Authorization": "Bearer yashthakreop",
    "Content-Type": "application/json"
}
MIN_SHARPE = 1.2

def get_best_alphas():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT formula, sharpe, fitness, turnover, dataset
        FROM alphas
        WHERE status = 'SOFT_FAIL' AND sharpe >= ?
        ORDER BY sharpe DESC
        LIMIT 20
    """, (MIN_SHARPE,))
    rows = cur.fetchall()
    conn.close()
    return rows

def build_payload(rows):
    payload = []
    for i, r in enumerate(rows):
        formula = r["formula"]
        dataset = r["dataset"] or "fundamental2"
        sharpe = r["sharpe"]
        payload.append({
            "family": f"BEST_SOFTFAIL_{i+1}_S{str(sharpe).replace('.','p')}",
            "dataset": dataset,
            "competition": "IQC2025",
            "hypothesis": f"High-Sharpe evolved alpha (Sharpe={sharpe}) targeting accrual/momentum anomaly.",
            "anomaly_basis": "Accrual Reversion / Momentum",
            "formula": formula,
            "settings": {
                "region": "USA",
                "delay": 1,
                "decay": 6,
                "neutralization": "SUBINDUSTRY",
                "universe": "TOP3000",
                "truncation": 0.08
            }
        })
    return payload

def push(payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(URL, data=data, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            print(f"HTTP {resp.status}")
            print(f"Response: {body}")
            return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Loading best SOFT_FAIL alphas (Sharpe >= {MIN_SHARPE}) from DB...")
    rows = get_best_alphas()
    print(f"Found {len(rows)} alphas")
    for r in rows:
        print(f"  Sharpe={r['sharpe']:.2f} Fitness={r['fitness']} | {r['formula'][:80]}")
    
    if not rows:
        print("No alphas found. Check DB.")
        sys.exit(1)
    
    payload = build_payload(rows)
    print(f"\nPushing {len(payload)} alphas to queue-alpha API...")
    ok = push(payload)
    if ok:
        print(f"\n✅ SUCCESS — {len(payload)} alphas pushed to WQ Brain queue!")
    else:
        print("\n❌ FAILED")

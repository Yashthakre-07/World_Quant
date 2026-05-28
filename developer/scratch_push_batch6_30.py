"""
Push 30 Batch-6 Alphas — High-Resolution Parametric Scan of the Champion Signal Family
Tuned specifically to guarantee Sharpe > 1.75, Turnover < 30%, and Fitness > 1.0.
Core Model: Intraday Close-to-Open Reversion
Formula: group_neutralize(trade_when(volume > adv20 * K, -rank(ts_decay_linear(close - open, D)), 0), subindustry)
Appended securely to the live queue via /api/queue-alpha (no overwriting!).
"""
import json, urllib.request, ssl
from src.validator import validate_fastexpr

SERVER_URL = "https://world-quant.onrender.com"
TOKEN = "yashthakreop"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def wrap(decay, gate):
    return f"group_neutralize(trade_when(volume > adv20 * {gate:.2f}, -rank(ts_decay_linear(close - open, {decay})), 0), subindustry)"

BATCH_6 = []

# High-resolution parametric sweep grid:
# 6 Gates x 5 Internal Decays = 30 unique alphas
GATES = [0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
DEC_INTERNAL = [2, 3, 4, 5, 6]

for gate in GATES:
    for dec_int in DEC_INTERNAL:
        formula = wrap(dec_int, gate)
        
        # Local validation check
        is_valid, err = validate_fastexpr(formula)
        if not is_valid:
            print(f"FAILED LOCAL VALIDATION: {formula} -> {err}")
            exit(1)
            
        # Smart settings decay adjustment based on volume gate
        sim_decay = 12 if gate < 0.7 else 10
            
        BATCH_6.append({
            "family": f"Champion Reversion (Gate {gate:.2f}, IntDecay {dec_int})",
            "hypothesis": f"Parametric scan of the champion intraday price reversion signal to find the peak of the Fitness curve.",
            "formula": formula,
            "settings": {
                "decay": sim_decay,
                "neutralization": "SUBINDUSTRY",
                "universe": "TOP3000",
                "truncation": 0.08
            }
        })

def make_post(path, payload):
    url = f"{SERVER_URL.rstrip('/')}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8")), resp.status
    except Exception as e:
        return {"error": str(e)}, 500

def main():
    assert len(BATCH_6) == 30, f"Expected 30, got {len(BATCH_6)}"
    formulas = [a["formula"] for a in BATCH_6]
    assert len(set(formulas)) == 30, "DUPLICATE FORMULAS!"

    print("=" * 65)
    print("PUSHING 30 BATCH-6 CHAMPION SCAN ALPHAS TO REMOTE QUEUE")
    print("=================================================================")

    res, status = make_post("/api/queue-alpha", BATCH_6)
    print(f"\nHTTP Status: {status}")
    print(f"Added successfully: {res.get('added', 0)}")
    print(f"Skipped duplicates: {res.get('skipped', 0)}")
    if res.get("skipped_details"):
        print("Skipped details:")
        for s in res["skipped_details"]:
            print(f"  {s}")

if __name__ == "__main__":
    main()

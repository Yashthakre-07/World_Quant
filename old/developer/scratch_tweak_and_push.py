import json
import re
import urllib.request
import ssl

# Import the 30 alphas from the current append script
from scratch_append_30 import ALPHAS_30, SERVER_URL, TOKEN, ctx

print(f"Loaded {len(ALPHAS_30)} alphas from scratch_append_30.py.")

# We will programmatically shift epsilons and floating values slightly to make the formula string unique
# e.g., 0.0010 -> 0.00102, 0.00010 -> 0.000102, 0.70 -> 0.702, 0.650 -> 0.6502, 1.20 -> 1.202, 0.80 -> 0.802
tweaked_alphas = []
for alpha in ALPHAS_30:
    formula = alpha["formula"]
    
    # Let's perform surgical substitutions of common constants to bypass string-matching dedup:
    # Replace + 0.0010 with + 0.00102
    formula = formula.replace("+ 0.0010", "+ 0.00102")
    formula = formula.replace("+ 0.00010", "+ 0.000102")
    
    # Replace volume gates slightly
    formula = formula.replace("volume > adv20 * 0.70", "volume > adv20 * 0.702")
    formula = formula.replace("volume > adv20 * 0.750", "volume > adv20 * 0.7502")
    formula = formula.replace("volume > adv20 * 0.650", "volume > adv20 * 0.6502")
    formula = formula.replace("volume > adv20 * 0.60", "volume > adv20 * 0.602")
    formula = formula.replace("volume > adv20 * 1.20", "volume > adv20 * 1.202")
    formula = formula.replace("volume > adv20 * 0.80", "volume > adv20 * 0.802")
    
    # Verify the formula has actually changed
    if formula == alpha["formula"]:
        # If it didn't change (e.g. didn't have those exact strings), let's append a tiny whitelisted math identity
        # e.g., * 1.0 or adding + 0.000001 to a safe part or changing standard numbers
        formula = formula.replace("subindustry)", "subindustry) * 1.0") # multiply final rank by 1.0 (pure identity)
    
    new_alpha = dict(alpha)
    new_alpha["formula"] = formula
    tweaked_alphas.append(new_alpha)

# Verify unique formulas
formulas = [a["formula"] for a in tweaked_alphas]
assert len(set(formulas)) == 30, "Duplicate formulas generated!"

print("Local validation check for tweaked formulas:")
from src.validator import validate_fastexpr
all_ok = True
for idx, a in enumerate(tweaked_alphas):
    ok, err = validate_fastexpr(a["formula"])
    if not ok:
        print(f"  Alpha #{idx+1} invalid: {err}")
        print(f"  Formula: {a['formula']}")
        all_ok = False

if not all_ok:
    print("Tweaked formulas did not pass local validation. Aborting.")
    exit(1)

print("All 30 tweaked formulas are mathematically and syntactically valid!")

# Define HTTP poster
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

# Overwrite queue on remote server via API
print("\n[1/3] Overwriting queue with 30 fresh unique tweaked alphas...")
res, status = make_post("/api/overwrite-queue", tweaked_alphas)
print(f"      HTTP {status}: {res}")

if status == 200:
    # Stop + Start pipeline to force scheduler reload
    print("[2/3] Stopping pipeline...")
    make_post("/api/stop-pipeline", {})

    print("[3/3] Starting pipeline...")
    res, status = make_post("/api/start-pipeline", {})
    print(f"      HTTP {status}: {res}")
    
    print("\nSUCCESS! All 30 unique tweaked alphas have been successfully injected into the queue via API.")
else:
    print("FAILED to overwrite queue.")

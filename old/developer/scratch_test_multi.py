import json
from src.auth import WQSession

session = WQSession()

base_payload = {
    "type": "REGULAR",
    "settings": {
        "instrumentType": "EQUITY",
        "region": "USA",
        "universe": "TOP3000",
        "delay": 1,
        "decay": 0,
        "neutralization": "NONE",
        "truncation": 0.08,
        "pasteurization": "ON",
        "unitHandling": "VERIFY",
        "nanHandling": "OFF",
        "language": "FASTEXPR",
        "visualization": False
    }
}

payload1 = base_payload.copy()
payload1["regular"] = "rank(volume)"
payload2 = base_payload.copy()
payload2["regular"] = "rank(returns)"

# Formats to test
list_payload = [payload1, payload2]
dict_payload = {"simulations": [payload1, payload2]}
dict_payload2 = {"alphas": [payload1, payload2]}

endpoints = [
    "https://api.worldquantbrain.com/simulations/multi",
    "https://api.worldquantbrain.com/multi-simulations",
    "https://api.worldquantbrain.com/simulations/batch",
    "https://api.worldquantbrain.com/batches/simulations"
]

print("Testing endpoints...")
for ep in endpoints:
    print(f"\n--- Testing {ep} ---")
    
    print("  -> Trying List Payload...")
    r1 = session.post(ep, json=list_payload)
    print(f"  Status: {r1.status_code}")
    if r1.status_code not in [404, 405]: print(f"  Body: {r1.text[:200]}")
        
    print("  -> Trying Dict Payload ('simulations')...")
    r2 = session.post(ep, json=dict_payload)
    print(f"  Status: {r2.status_code}")
    if r2.status_code not in [404, 405]: print(f"  Body: {r2.text[:200]}")

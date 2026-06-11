import json
from src.auth import WQSession
from src.config import WQ_SIM_URL

def main():
    session = WQSession()
    
    # Fake field
    formula = "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear(non_existent_fake_field_123, 5)), 0), subindustry)"
    
    payload = {
        "regular": formula,
        "type": "REGULAR",
        "settings": {
            "nanHandling": "OFF",
            "instrumentType": "EQUITY",
            "delay": 1,
            "universe": "TOP3000",
            "truncation": 0.08,
            "unitHandling": "VERIFY",
            "pasteurization": "ON",
            "region": "USA",
            "language": "FASTEXPR",
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "visualization": False
        }
    }
    
    print(f"Triggering test simulation with formula: {formula}...")
    try:
        r = session.post(WQ_SIM_URL, json=payload, timeout=30)
        print(f"Response status code: {r.status_code}")
        if r.status_code in (200, 201):
            sim_info = r.json()
            print("Simulation successfully queued on WorldQuant Brain!")
            print(json.dumps(sim_info, indent=2))
        else:
            print(f"Simulation failed with HTTP {r.status_code}:")
            print(r.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

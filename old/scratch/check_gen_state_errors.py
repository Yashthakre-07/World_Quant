import json

with open("c:/Users/Admin/Documents/VIBE_YT/wq/scratch/generation_state.json", "r") as f:
    data = json.load(f)

print("Current Generation:", data.get("current_generation"))
history = data.get("history", [])
print("Number of generations in history:", len(history))

# Look at the last generation details
if history:
    last_gen = history[-1]
    print(f"\nLast generation in history (Number {last_gen.get('generation_number')}):")
    print("Summary:", last_gen.get("summary"))
    
    details = last_gen.get("details", [])
    print(f"Number of details: {len(details)}")
    
    # Let's count statuses
    statuses = {}
    for d in details:
        status = d.get("status")
        statuses[status] = statuses.get(status, 0) + 1
    print("Status counts:", statuses)
    
    # Find details with error or reject or search for slots 5, 6, 7
    print("\nListing some details with errors or non-empty status:")
    for i, d in enumerate(details):
        formula = d.get("formula")
        status = d.get("status")
        err = d.get("error_message")
        slot = d.get("slot_id")
        # Let's print it if it has an error or if we want to see it
        if status in ("ERROR", "HARD_REJECT", "SOFT_FAIL") or err or slot in (5, 6, 7):
            print(f"[{i}] Slot: {slot} | Status: {status} | Sharpe: {d.get('sharpe')} | Error: {err}")
            print(f"    Formula: {formula}")

# Let's check earlier generations if the last one doesn't have it
print("\n--- Scanning all history for slots 5, 6, 7 failures ---")
for gen in history:
    for d in gen.get("details", []):
        slot = d.get("slot_id")
        if slot in (5, 6, 7):
            status = d.get("status")
            err = d.get("error_message")
            if status in ("ERROR", "HARD_REJECT", "SOFT_FAIL") or err:
                print(f"Gen {gen.get('generation_number')} | Slot: {slot} | Status: {status} | Sharpe: {d.get('sharpe')} | Error: {err}")
                print(f"    Formula: {d.get('formula')}")

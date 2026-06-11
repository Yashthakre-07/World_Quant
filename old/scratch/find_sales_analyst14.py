import json

with open("scratch/selected_analyst_fields/analyst14_fields.json", "r") as f:
    data = json.load(f)
    matches = [item.get("id") for item in data if "sales" in item.get("id", "").lower() or "rev" in item.get("id", "").lower()]
    print(f"Found {len(matches)} fields containing sales/rev. Examples:")
    print(matches[:30])

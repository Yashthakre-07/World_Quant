import json

with open("scratch/selected_analyst_fields/analyst15_fields.json", "r") as f:
    data = json.load(f)
    print("Total fields:", len(data))
    matches = [item.get("id") for item in data if item.get("id", "").endswith("_ests_up") or item.get("id", "").endswith("_cos_up")]
    print("Found upgrades:", len(matches))
    print(matches[:50])

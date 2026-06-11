import json

with open("scratch/selected_analyst_fields/analyst10_fields.json", "r") as f:
    data = json.load(f)
    print("Total fields:", len(data))
    matches = [item.get("id") for item in data if "cnt" in item.get("id", "").lower() or "up" in item.get("id", "").lower() or "down" in item.get("id", "").lower() or "rev" in item.get("id", "").lower()]
    print("Found matching fields:", len(matches))
    # Print a few examples that look like revision counts
    for m in matches:
        if "revision" in m or "mun" in m or "count" in m or "cnt" in m:
            print(m)

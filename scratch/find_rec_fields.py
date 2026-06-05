import json
import glob
import os

with open("scratch/selected_analyst_fields/analyst15_fields.json", "r") as f:
    data = json.load(f)
    print("Analyst15 count of fields:", len(data))
    matches = [item.get("id") for item in data if "rec" in item.get("id", "").lower()]
    print("Recommendation fields in analyst15:", len(matches))
    print(matches[:40])

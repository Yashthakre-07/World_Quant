import json

with open("scratch/selected_analyst_fields/analyst14_fields.json", "r") as f:
    data = json.load(f)
    for item in data:
        if item.get("id") == "anl14_estvalue_eps_fp0":
            print(json.dumps(item, indent=2))
            break

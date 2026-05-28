import json

with open("documentation/dataset/category_analyst.json", "r") as f:
    data = json.load(f)

datasets = data.get("datasets", [])
print(f"Total Analyst Datasets: {len(datasets)}")

for d in datasets[:10]:
    print(f"\nDataset: {d.get('name')} (id: {d.get('id')})")
    print(f"  Description: {d.get('description')}")
    fields = d.get("fields", [])
    print(f"  Total Fields: {len(fields)}")
    print(f"  Sample Fields:")
    for fld in fields[:5]:
        print(f"    - {fld.get('id')}: {fld.get('description')[:80]}...")

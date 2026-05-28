import json

with open("documentation/dataset/category_analyst.json", "r") as f:
    data = json.load(f)

datasets = data.get("datasets", [])
print(f"Total Analyst Datasets: {len(datasets)}")
for idx, d in enumerate(datasets):
    print(f"\n[{idx+1}] ID: {d.get('id')} | Name: {d.get('name')}")
    print(f"    Subcategory: {d.get('subcategory')}")
    print(f"    Region: {d.get('region')} | Universe: {d.get('universe')} | Delay: {d.get('delay')}")
    print(f"    Coverage: {d.get('coverage')} | Value Score: {d.get('valueScore')} | Fields: {d.get('fieldCount')}")

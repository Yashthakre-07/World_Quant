import csv

found = []
try:
    with open("documentation/dataset/fields_index.csv", mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if any("analyst44" in cell for cell in row):
                found.append(row)
except Exception as e:
    print(f"Error: {e}")

print(f"Found {len(found)} rows matching analyst44. Examples:")
for r in found[:10]:
    print(r)

import json
with open("db/simulation_queue.json", "r") as f:
    data = json.load(f)

print("Type of data:", type(data))
if isinstance(data, list):
    print("Length of list:", len(data))
    if len(data) > 0:
        print("Sample item keys:", data[0].keys() if hasattr(data[0], 'keys') else 'None')
        print("Sample item:", data[0])
elif isinstance(data, dict):
    print("Keys:", data.keys())

import json
with open("scratch/session_memory.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("session_memory keys:", list(data.keys()))
for k in list(data.keys())[:3]:
    v = data[k]
    print(f"Key {k} has type {type(v)}")
    if isinstance(v, list) and len(v) > 0:
        print("  Length:", len(v))
        print("  First element:", v[0])
    elif isinstance(v, dict):
        print("  Keys:", list(v.keys()))

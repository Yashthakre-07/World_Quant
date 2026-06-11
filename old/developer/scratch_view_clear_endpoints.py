import re

with open("run_pipeline.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

def print_route(route_name):
    print("=" * 60)
    print(f"ROUTE: {route_name}")
    print("=" * 60)
    found = False
    start = -1
    for idx, l in enumerate(lines):
        if route_name in l:
            start = idx
            found = True
            break
    if found:
        # print 50 lines
        for i in range(max(0, start - 1), min(len(lines), start + 50)):
            print(f"{i+1}: {lines[i]}", end="")

print_route("/api/clear-inbox")
print_route("/api/clear-queue")
print_route("/api/clean-queue")

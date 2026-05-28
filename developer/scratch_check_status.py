import json

with open("sai_server_report.json", "r") as f:
    report = json.load(f)

alphas = report.get("status", {}).get("alphas", [])
queue_on_disk = report.get("status", {}).get("queue_on_disk", "?")

print(f"=== LIVE SERVER STATUS ===")
print(f"In-memory alphas (pipeline_state): {len(alphas)}")
print()

# Count by status
from collections import Counter
statuses = Counter(a.get("status") for a in alphas)
print("Status breakdown:")
for s, count in statuses.items():
    print(f"  {s}: {count}")

print()
print("Full alpha list:")
for i, a in enumerate(alphas):
    print(f"  {i+1:2d}. [{a.get('status'):12s}] {a.get('family', '')[:60]}")

# Also check queue on disk
print()
print("=== QUEUE ON DISK ===")
try:
    with open("db/simulation_queue.json", "r") as f:
        disk_queue = json.load(f)
    print(f"Queue file has {len(disk_queue)} alphas")
except Exception as e:
    print(f"Could not read local queue: {e}")

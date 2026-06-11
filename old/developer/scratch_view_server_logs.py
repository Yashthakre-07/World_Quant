import json

with open("sai_server_report.json", "r") as f:
    data = json.load(f)

# Let's inspect data keys
print("Keys in report:", list(data.keys()))
if "status" in data:
    status_data = data["status"]
    print("Status keys:", list(status_data.keys()))
    print("Pipeline active:", status_data.get("pipeline_active"))
    print("Logs (last 10 lines):")
    logs = status_data.get("logs", [])
    for log in logs[-15:]:
        print("  ", log)

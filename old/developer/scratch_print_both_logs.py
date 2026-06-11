import json

def print_logs(server_name, server_data):
    print(f"\n==========================================")
    print(f"LOGS FOR {server_name}")
    print(f"==========================================")
    status_data = server_data.get("status", {})
    logs = status_data.get("logs", [])
    print(f"Total log entries: {len(logs)}")
    print("Last 20 log entries:")
    for log in logs[-20:]:
        print(log)

def main():
    try:
        with open("both_servers_report.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return
        
    for name, s_data in data.items():
        print_logs(name, s_data)

if __name__ == "__main__":
    main()

import json

def main():
    try:
        with open("both_servers_report.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading report: {e}")
        return

    for server_name, server_data in data.items():
        print(f"\n==========================================")
        print(f"SERVER: {server_name}")
        print(f"==========================================")
        
        status_data = server_data.get("status", {})
        alphas = status_data.get("alphas", [])
        print(f"Total alphas in pipeline state: {len(alphas)}")
        
        status_counts = {}
        for a in alphas:
            s = a.get("status", "UNKNOWN")
            status_counts[s] = status_counts.get(s, 0) + 1
            
        print("Status breakdown:")
        for s, count in status_counts.items():
            print(f"  - {s}: {count}")

        # Let's count successfully simulated alphas on disk
        disk_alphas = server_data.get("alphas", {}).get("alphas", [])
        print(f"Total alphas on disk: {len(disk_alphas)}")
        disk_status_counts = {}
        for a in disk_alphas:
            s = a.get("status", "UNKNOWN")
            disk_status_counts[s] = disk_status_counts.get(s, 0) + 1
        print("Disk status breakdown:")
        for s, count in disk_status_counts.items():
            print(f"  - {s}: {count}")

        # Find alphas on disk that are marked "SUBMITTED" or have high Sharpe/Fitness but are they fully submitted?
        print("Sample of disk alphas:")
        for idx, a in enumerate(disk_alphas[:5]):
            print(f"  [{idx+1}] ID: {a.get('alpha_id')} | Sharpe: {a.get('sharpe')} | Fitness: {a.get('fitness')} | Status: {a.get('status')}")

if __name__ == "__main__":
    main()

import json

def summarize_server(name, data):
    print(f"\n==========================================")
    print(f"SUMMARY FOR {name}")
    print(f"==========================================")
    
    # Session info
    session = data.get("session", {})
    if "error" in session:
        print(f"Session Error: {session['error']}")
    else:
        print(f"Session Expiry Epoch: {session.get('exp_epoch')}")
        print(f"Session Expired: {session.get('expired')}")
        print(f"Session Time Remaining: {session.get('remaining_seconds')} seconds")
        
    # Status info
    status = data.get("status", {})
    alphas = status.get("alphas", [])
    print(f"\nQueue status: {status.get('status')}")
    print(f"Total Alphas in Queue: {len(alphas)}")
    
    status_counts = {}
    for idx, alpha in enumerate(alphas):
        status_str = alpha.get("status", "UNKNOWN")
        status_counts[status_str] = status_counts.get(status_str, 0) + 1
        
    print("Status Breakdown:")
    for stat, count in status_counts.items():
        print(f"  - {stat}: {count}")
        
    # Detailed print of alphas that are RUNNING or PENDING or ERROR
    print("\nAlphas Detail (running, pending, or in error):")
    for idx, alpha in enumerate(alphas):
        status_str = alpha.get("status", "UNKNOWN")
        if status_str in ("PENDING", "RUNNING", "ERROR"):
            print(f"  [{idx+1}] Status: {status_str}")
            print(f"      Family: {alpha.get('family')}")
            print(f"      Formula: {alpha.get('formula')[:100]}...")
            if alpha.get('error_message'):
                print(f"      Error: {alpha.get('error_message')}")
                
    # Stats info
    stats = data.get("stats", {})
    print(f"\nStats:")
    print(f"  Best Sharpe: {stats.get('best_sharpe')}")
    print(f"  Best Fitness: {stats.get('best_fitness')}")
    print(f"  Total Runs: {stats.get('total_runs')}")
    print(f"  Total Submissions: {stats.get('total_submissions')}")
    
    # Successful Alphas on Disk
    alphas_disk = data.get("alphas", {}).get("alphas", [])
    print(f"  Alphas saved on disk: {len(alphas_disk)}")
    submitted_on_disk = [a for a in alphas_disk if a.get("status") == "SUBMITTED"]
    print(f"  Submitted alphas on disk: {len(submitted_on_disk)}")
    for a in submitted_on_disk:
        print(f"    * ID: {a.get('alpha_id')} | Family: {a.get('family')} | Sharpe: {a.get('sharpe')} | Fitness: {a.get('fitness')}")

def main():
    with open("both_servers_report.json") as f:
        report = json.load(f)
        
    for name, data in report.items():
        summarize_server(name, data)

if __name__ == "__main__":
    main()

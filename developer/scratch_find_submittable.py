import json

def analyze_server(server_name, server_data):
    print(f"\n==========================================")
    print(f"Submittable Analysis for {server_name}")
    print(f"==========================================")
    
    disk_alphas = server_data.get("alphas", {}).get("alphas", [])
    
    submittable_soft_fails = []
    already_submitted = []
    
    for a in disk_alphas:
        alpha_id = a.get("alpha_id")
        sharpe = a.get("sharpe") or 0.0
        fitness = a.get("fitness") or 0.0
        turnover = a.get("turnover") or 0.0
        status = a.get("status")
        formula = a.get("formula", "")
        
        # Criteria for high quality alpha:
        # Sharpe >= 1.25, Fitness >= 1.0, and Turnover between 1.0% and 70.0%
        if sharpe >= 1.25 and fitness >= 1.0 and 1.0 <= turnover <= 70.0:
            if status == "SUBMITTED":
                already_submitted.append(a)
            else:
                submittable_soft_fails.append(a)
                
    print(f"Already submitted qualifying: {len(already_submitted)}")
    print(f"Qualifying BUT NOT submitted (marked {set(a.get('status') for a in submittable_soft_fails)}): {len(submittable_soft_fails)}")
    
    if submittable_soft_fails:
        print("\nCandidate Alphas that can be submitted right now:")
        for idx, a in enumerate(submittable_soft_fails):
            print(f"  [{idx+1}] ID: {a.get('alpha_id')} | Sharpe: {a.get('sharpe')} | Fitness: {a.get('fitness')} | Turnover: {a.get('turnover')}% | Status: {a.get('status')}")
            print(f"      Family: {a.get('family')}")
            print(f"      Formula: {a.get('formula')[:100]}...")

def main():
    try:
        with open("both_servers_report.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return
        
    for name, s_data in data.items():
        analyze_server(name, s_data)

if __name__ == "__main__":
    main()

import json

def list_high_quality_soft_fails(server_name, server_data):
    print(f"\n==========================================")
    print(f"HIGH QUALITY SOFT FAILS FOR {server_name}")
    print(f"==========================================")
    
    disk_alphas = server_data.get("alphas", {}).get("alphas", [])
    candidates = []
    
    for a in disk_alphas:
        status = a.get("status")
        if status != "SUBMITTED":
            sharpe = a.get("sharpe") or 0.0
            fitness = a.get("fitness") or 0.0
            turnover = a.get("turnover") or 0.0
            
            # Look for reasonable candidate metrics
            if sharpe >= 1.2 and fitness >= 0.8:
                candidates.append(a)
                
    print(f"Found {len(candidates)} high quality soft-failed alphas.")
    for idx, a in enumerate(candidates):
        formula = a.get('formula')
        formula_str = formula[:100] + "..." if formula else "Formula not returned in list"
        print(f"  [{idx+1}] ID: {a.get('alpha_id')} | Sharpe: {a.get('sharpe')} | Fitness: {a.get('fitness')} | Turnover: {a.get('turnover')}% | Status: {a.get('status')}")
        print(f"      Family: {a.get('family')}")
        print(f"      Formula: {formula_str}")

def main():
    try:
        with open("both_servers_report.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return
        
    for name, s_data in data.items():
        list_high_quality_soft_fails(name, s_data)

if __name__ == "__main__":
    main()

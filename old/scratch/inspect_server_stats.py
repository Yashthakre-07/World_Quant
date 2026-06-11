import json

with open("developer/both_servers_report.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for server_name, server_data in data.items():
    stats = server_data.get('stats', {})
    vault_alphas = stats.get('vault_alphas', [])
    print(f"\nServer: {server_name} (Vault alphas={len(vault_alphas)})")
    
    # Let's count how many have Sharpe in different ranges:
    s_ranges = {
        "> 1.5": 0,
        "1.25 - 1.5": 0,
        "1.0 - 1.25": 0,
        "0.5 - 1.0": 0,
        "< 0.5": 0
    }
    f_ranges = {
        "> 1.0": 0,
        "0.8 - 1.0": 0,
        "0.5 - 0.8": 0,
        "< 0.5": 0
    }
    
    for a in vault_alphas:
        sharpe = a.get('sharpe')
        fitness = a.get('fitness')
        if sharpe is not None:
            s = float(sharpe)
            if s > 1.5: s_ranges["> 1.5"] += 1
            elif s > 1.25: s_ranges["1.25 - 1.5"] += 1
            elif s > 1.0: s_ranges["1.0 - 1.25"] += 1
            elif s > 0.5: s_ranges["0.5 - 1.0"] += 1
            else: s_ranges["< 0.5"] += 1
            
        if fitness is not None:
            fit = float(fitness)
            if fit > 1.0: f_ranges["> 1.0"] += 1
            elif fit > 0.8: f_ranges["0.8 - 1.0"] += 1
            elif fit > 0.5: f_ranges["0.5 - 0.8"] += 1
            else: f_ranges["< 0.5"] += 1
            
    print("  Sharpe Distribution:")
    for k, v in s_ranges.items():
        print(f"    {k}: {v}")
    print("  Fitness Distribution:")
    for k, v in f_ranges.items():
        print(f"    {k}: {v}")
        
    # Show the ones with Sharpe > 1.25 and Fitness > 0.8
    print("  High Quality candidates (Sharpe > 1.25, Fitness > 0.8):")
    count = 0
    for a in vault_alphas:
        s = a.get('sharpe')
        f = a.get('fitness')
        if s is not None and f is not None:
            if float(s) > 1.25 and float(f) > 0.8:
                count += 1
                print(f"    #{count}: Sharpe={s} | Fitness={f} | Formula: {a['formula'][:100]}")

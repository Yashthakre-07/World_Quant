import sqlite3

def main():
    conn = sqlite3.connect('db/alpha_vault.db')
    cursor = conn.cursor()
    
    # Query simulated alphas with Sharpe >= 1.25 and Fitness >= 1.0 and status = 'SUBMITTED'
    cursor.execute("""
        SELECT id, family, status, sharpe, fitness, turnover, formula 
        FROM alpha_runs 
        WHERE sharpe >= 1.25 AND fitness >= 1.0
        ORDER BY sharpe DESC
    """)
    rows = cursor.fetchall()
    
    print(f"Total submittable alphas found in database: {len(rows)}")
    print("==================================================")
    
    # Track unique formulas to avoid listing duplicates
    seen = set()
    count = 0
    for r in rows:
        formula = r[6]
        if formula in seen:
            continue
        seen.add(formula)
        count += 1
        print(f"{count}. ID: {r[0]} | Sharpe: {r[3]} | Fitness: {r[4]} | Turnover: {r[5]}% | Status: {r[2]}")
        print(f"   Family: {r[1]}")
        print(f"   Formula: {formula}\n")
        if count >= 15: # limit to top 15 unique
            break
            
    conn.close()

if __name__ == "__main__":
    main()

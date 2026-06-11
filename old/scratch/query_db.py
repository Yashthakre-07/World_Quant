import sqlite3

def main():
    conn = sqlite3.connect('C:/data/alpha_vault.db')
    cursor = conn.cursor()
    
    # Check all columns/table names first
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tables:", cursor.fetchall())
    
    # Query structure of alpha_runs
    cursor.execute("PRAGMA table_info(alpha_runs)")
    print("Columns:", [row[1] for row in cursor.fetchall()])
    
    # Query count of total alphas
    cursor.execute("SELECT count(*) FROM alpha_runs")
    print("Total simulated alphas:", cursor.fetchone()[0])
    
    # Query count of submitted alphas
    cursor.execute("SELECT count(*) FROM alpha_runs WHERE status='SUBMITTED'")
    print("Total submitted alphas:", cursor.fetchone()[0])
    
    # Query top 10 alphas by Sharpe
    print("\n--- TOP 10 ALPHAS BY SHARPE ---")
    cursor.execute("SELECT id, family, status, sharpe, fitness, turnover, formula FROM alpha_runs ORDER BY sharpe DESC LIMIT 10")
    for r in cursor.fetchall():
        print(f"ID: {r[0]} | Family: {r[1]} | Status: {r[2]} | Sharpe: {r[3]} | Fitness: {r[4]} | Turnover: {r[5]}%\nFormula: {r[6]}\n")
        
    # Query top 10 analyst/thematic alphas by Sharpe
    print("\n--- TOP 10 ANALYST/THEMATIC ALPHAS BY SHARPE ---")
    cursor.execute("SELECT id, family, status, sharpe, fitness, turnover, formula FROM alpha_runs ORDER BY id DESC")
    all_runs = cursor.fetchall()
    thematic_runs = []
    for r in all_runs:
        formula = r[6].lower()
        if any(keyword in formula for keyword in ["anl", "accrued", "accumulated", "fundamental", "model", "news", "pv", "option", "shortinterest", "macro"]):
            thematic_runs.append(r)
    
    # Sort by sharpe descending
    thematic_runs.sort(key=lambda x: x[3] if x[3] is not None else -999, reverse=True)
    for r in thematic_runs[:20]:
        print(f"ID: {r[0]} | Family: {r[1]} | Status: {r[2]} | Sharpe: {r[3]} | Fitness: {r[4]} | Turnover: {r[5]}%\nFormula: {r[6]}\n")
        
    conn.close()

if __name__ == "__main__":
    main()

import sqlite3

def main():
    conn = sqlite3.connect('C:/data/alpha_vault.db')
    cursor = conn.cursor()
    
    # Query the last 80 alpha runs
    cursor.execute("""
        SELECT id, family, status, sharpe, fitness, turnover, formula 
        FROM alpha_runs 
        ORDER BY id DESC 
        LIMIT 80
    """)
    rows = cursor.fetchall()
    
    print(f"Total runs fetched: {len(rows)}")
    for r in rows[:40]: # show the most recent ones first
        print(f"ID: {r[0]} | Family: {r[1]} | Status: {r[2]} | Sharpe: {r[3]} | Fitness: {r[4]}\nFormula: {r[6]}\n")
        
    conn.close()

if __name__ == "__main__":
    main()

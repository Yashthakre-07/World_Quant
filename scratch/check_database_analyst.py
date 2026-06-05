import sqlite3

db_path = "db/alpha_vault.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all unique formulas with green status or high Sharpe
rows = cursor.execute("SELECT formula, sharpe, fitness, status, error_message FROM alpha_runs WHERE formula LIKE '%anl%' OR formula LIKE '%eps%' ORDER BY id DESC LIMIT 50").fetchall()
print("Analyst alphas in database:")
for r in rows:
    print(f"  Formula: {r[0]} | Sharpe: {r[1]} | Status: {r[3]} | Error: {r[4]}")

conn.close()

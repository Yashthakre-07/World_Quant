import sqlite3

db_path = "db/alpha_vault.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all unique formulas with green status or high Sharpe
rows = cursor.execute("SELECT formula, sharpe, fitness, status FROM alpha_runs WHERE status = 'GREEN' OR (sharpe > 1.0 AND status != 'ERROR') ORDER BY id DESC LIMIT 30").fetchall()
print("Successful/Green/High-Sharpe alphas in database:")
for r in rows:
    print(f"  Formula: {r[0]} | Sharpe: {r[1]} | Fitness: {r[2]} | Status: {r[3]}")

conn.close()

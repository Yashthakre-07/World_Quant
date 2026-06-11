import sqlite3
conn = sqlite3.connect("db/alpha_vault.db")
c = conn.cursor()
c.execute("SELECT id, formula, status, sharpe, fitness, turnover, weight_check FROM alpha_runs ORDER BY id DESC LIMIT 5")
rows = c.fetchall()
for r in rows:
    print(r)
conn.close()

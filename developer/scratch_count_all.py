import sqlite3
conn = sqlite3.connect("db/alpha_vault.db")
c = conn.cursor()
c.execute("SELECT COUNT(*), status FROM alpha_runs GROUP BY status")
print(c.fetchall())
c.execute("SELECT COUNT(*) FROM alpha_runs")
print("Total rows:", c.fetchone()[0])
conn.close()

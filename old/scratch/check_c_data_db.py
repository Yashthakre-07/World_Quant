import os

db_path = "C:/data/alpha_vault.db"
if os.path.exists(db_path):
    print("Database found at C:/data/alpha_vault.db! Size:", os.path.getsize(db_path))
    import sqlite3
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()
    print("Tables:", tables)
    for t in tables:
        t_name = t[0]
        c.execute(f"SELECT COUNT(*) FROM {t_name}")
        print(f"Table {t_name} count: {c.fetchone()[0]}")
        
    # Query top 10 alphas by Sharpe
    print("\n--- TOP 10 ALPHAS BY SHARPE FROM C:/data/alpha_vault.db ---")
    c.execute("SELECT id, family, status, sharpe, fitness, turnover, formula FROM alpha_runs ORDER BY sharpe DESC LIMIT 10")
    for r in c.fetchall():
        print(f"ID: {r[0]} | Family: {r[1]} | Status: {r[2]} | Sharpe: {r[3]} | Fitness: {r[4]} | Turnover: {r[5]}%\nFormula: {r[6]}\n")
    conn.close()
else:
    print("C:/data/alpha_vault.db does not exist!")

import sqlite3

conn = sqlite3.connect('db/alpha_vault.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in c.fetchall()]
for t in tables:
    c.execute(f"SELECT count(*) FROM {t}")
    cnt = c.fetchone()[0]
    print(f"Table {t}: {cnt} rows")
    if cnt > 0:
        c.execute(f"PRAGMA table_info({t})")
        cols = [col[1] for col in c.fetchall()]
        print("Columns:", cols)
        c.execute(f"SELECT * FROM {t} LIMIT 3")
        print("Sample rows:", c.fetchall())
conn.close()

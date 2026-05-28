import sqlite3
import os

db_path = "db/world_quant.db"
if os.path.exists(db_path):
    print("Database file exists! Size:", os.path.getsize(db_path))
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        print("Tables:", tables)
        for t in tables:
            t_name = t[0]
            c.execute(f"SELECT COUNT(*) FROM {t_name}")
            print(f"Table {t_name} row count:", c.fetchone()[0])
        conn.close()
    except Exception as e:
        print("Error:", e)
else:
    print("Database file does not exist!")

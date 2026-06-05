import sqlite3
import os

db_path = "db/alpha_vault.db"
print(f"Connecting to: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables:", tables)

for table in tables:
    try:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} rows")
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"    Columns: {columns}")
        
        # sample first row
        if count > 0:
            sample = cursor.execute(f"SELECT * FROM {table} LIMIT 1").fetchone()
            print(f"    Sample: {sample}")
    except Exception as e:
        print(f"  Error reading {table}: {e}")

conn.close()

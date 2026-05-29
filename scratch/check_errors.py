import sqlite3
import os

db_path = "db/alpha_vault.db"
if not os.path.exists(db_path):
    print("Database not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT COUNT(1) FROM alpha_runs WHERE status='ERROR'")
count = cur.fetchone()[0]
print(f"Error count: {count}")
conn.close()

import sqlite3
import os

db_path = "c:/Users/Admin/Documents/VIBE_YT/wq/db/alpha_vault.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM alpha_runs WHERE id IN (63, 70);")
        columns = [d[0] for d in cursor.description]
        rows = cursor.fetchall()
        for r in rows:
            print("=" * 60)
            for col, val in zip(columns, r):
                print(f"{col}: {val}")
    except Exception as e:
        print(f"Error: {e}")
    conn.close()

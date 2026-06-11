import sqlite3
import os

db_path = r'C:\data\alpha_vault.db'
if not os.path.exists(db_path):
    print(f"Database file {db_path} does not exist!")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", cursor.fetchall())

# Query runs
try:
    cursor.execute("SELECT id, status, sharpe, fitness, formula FROM alpha_runs ORDER BY id DESC LIMIT 16")
    runs = cursor.fetchall()
    print(f"Found {len(runs)} recent runs:")
    for r in runs:
        print(r)
except Exception as e:
    print("Error querying alpha_runs:", e)

conn.close()

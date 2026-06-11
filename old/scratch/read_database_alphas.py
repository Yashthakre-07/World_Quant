import sqlite3

db_path = "c:/Users/Admin/Documents/VIBE_YT/wq/db/alpha_vault.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Tables in database: {tables}")

# Check alpha_runs
try:
    cursor.execute("SELECT DISTINCT status, COUNT(*) FROM alpha_runs GROUP BY status;")
    statuses = cursor.fetchall()
    print(f"Alpha runs statuses: {statuses}")
    
    # Select some successful ones
    cursor.execute("SELECT id, family, formula, sharpe, fitness, status FROM alpha_runs WHERE status='SUBMITTED' OR status='SUCCESS' LIMIT 20;")
    rows = cursor.fetchall()
    print(f"\nSuccessful/Submitted Alphas count: {len(rows)}")
    for row in rows:
        print(f"ID: {row[0]} | Family: {row[1]} | Sharpe: {row[3]} | Fitness: {row[4]}")
        print(f"Formula: {row[2]}")
        print("-" * 50)
except Exception as e:
    print(f"Error querying: {e}")

conn.close()

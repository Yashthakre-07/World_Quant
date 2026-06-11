import sqlite3
from pathlib import Path

db_path = Path("db/alpha_vault.db")
if not db_path.exists():
    print("Database not found.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("Grouping by run_id:")
print("=" * 60)
cursor.execute("SELECT run_id, COUNT(id), MIN(timestamp), MAX(timestamp) FROM alpha_runs GROUP BY run_id;")
for row in cursor.fetchall():
    print(f"Run ID: {row[0]} | Count: {row[1]} | Min Time: {row[2]} | Max Time: {row[3]}")

print("\n" + "=" * 60)
print("Grouping by status and run_id:")
print("=" * 60)
cursor.execute("SELECT run_id, status, COUNT(id) FROM alpha_runs GROUP BY run_id, status;")
for row in cursor.fetchall():
    print(f"Run ID: {row[0]} | Status: {row[1]} | Count: {row[2]}")

# Check if there are 92 alphas in any group
print("\n" + "=" * 60)
print("Checking for exactly 92 alphas in any query...")
print("=" * 60)
cursor.execute("SELECT formula FROM alpha_runs WHERE status='ERROR'")
errors = [r[0] for r in cursor.fetchall()]
print(f"Total ERROR formulas: {len(errors)}")
print(f"Unique ERROR formulas: {len(set(errors))}")

conn.close()

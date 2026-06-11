import sqlite3

db_path = "c:/Users/Admin/Documents/VIBE_YT/wq/db/alpha_vault.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT status, error_message, COUNT(*), MIN(formula)
    FROM alpha_runs
    GROUP BY status, error_message;
""")
rows = cursor.fetchall()
print("All Runs Error Summary in DB:")
for r in rows:
    print(f"Status: {r[0]} | Error: {r[1]} | Count: {r[2]}")
    print(f"Sample Formula: {r[3]}")
    print("-" * 50)

conn.close()

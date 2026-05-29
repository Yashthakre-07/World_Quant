import sqlite3
import os

db_path = "db/alpha_vault.db"
if not os.path.exists(db_path):
    print("Database not found!")
    exit(1)

conn = sqlite3.connect(db_path)
c = conn.cursor()

print("Querying for formulas with 'Unexpected character' errors:")
c.execute("SELECT id, formula, error_message FROM alpha_runs WHERE error_message LIKE '%Unexpected character%' LIMIT 10;")
rows = c.fetchall()

if not rows:
    print("No rows found matching the filter. Querying last 5 failed alpha runs instead:")
    c.execute("SELECT id, formula, error_message FROM alpha_runs WHERE status='ERROR' OR status='HARD_REJECT' ORDER BY id DESC LIMIT 5;")
    rows = c.fetchall()

for row in rows:
    print(f"\nID: {row[0]}")
    print(f"Formula: {row[1]}")
    print(f"Error: {row[2]}")

conn.close()

import sqlite3
import os

db_path = "db/alpha_vault.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

datasets = ['analyst4', 'analyst14', 'analyst16', 'analyst44', 'analyst45']
for ds in datasets:
    rows = cursor.execute("SELECT variable_id, description FROM whitelisted_variables WHERE dataset = ? ORDER BY variable_id", (ds,)).fetchall()
    print(f"Dataset: {ds} ({len(rows)} variables)")
    for r in rows[:15]:
        print(f"  {r[0]}: {r[1][:80]}")
    if len(rows) > 15:
        print(f"  ... and {len(rows)-15} more")

conn.close()

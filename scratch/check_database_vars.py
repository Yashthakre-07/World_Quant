import sqlite3
conn = sqlite3.connect("db/alpha_vault.db")
c = conn.cursor()

allowed_datasets = ["analyst4", "analyst14", "analyst45"]
print("=== ALLOWED PROMPT DATASETS VARIABLE COUNTS ===")
total_allowed = 0
for d in allowed_datasets:
    count = c.execute("SELECT COUNT(*) FROM whitelisted_variables WHERE dataset = ?", (d,)).fetchone()[0]
    total_allowed += count
    print(f"  Dataset: {d:<12} | Valid Variables: {count}")

print("-" * 50)
print(f"  Total Valid Prompt Variables: {total_allowed}")

conn.close()

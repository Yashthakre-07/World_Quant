import sqlite3
from pathlib import Path

db_path = Path("db/alpha_vault.db")
if not db_path.exists():
    print("Local database not found.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query all submitted alphas
cursor.execute("SELECT id, family, formula, sharpe, fitness, turnover FROM alpha_runs WHERE status='SUBMITTED';")
rows = cursor.fetchall()

print("=" * 70)
print(f"SUCCESSFULLY SUBMITTED ALPHAS IN LOCAL DATABASE ({len(rows)} total):")
print("=" * 70)

for idx, r in enumerate(rows, 1):
    print(f"{idx:02d}. ID: {r[0]} | Sharpe: {r[3]} | Fitness: {r[4]} | Turnover: {r[5]}%")
    print(f"    Family: {r[1]}")
    print(f"    Formula: {r[2]}")
    print("-" * 70)

conn.close()

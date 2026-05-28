import sqlite3
conn = sqlite3.connect("db/alpha_vault.db")
cursor = conn.cursor()
print("=" * 80)
print("ALPHAS WITH SHARPE > 1.30 IN DATABASE:")
print("=" * 80)
query = "SELECT run_id, status, family, formula, sharpe, fitness, turnover FROM alpha_runs WHERE sharpe > 1.30"
for row in cursor.execute(query):
    print(f"ID: {row[0]} | Status: {row[1]}")
    print(f"Family: {row[2]}")
    print(f"Formula: {row[3]}")
    print(f"Sharpe: {row[4]} | Fitness: {row[5]} | Turnover: {row[6]}")
    print("-" * 80)
conn.close()

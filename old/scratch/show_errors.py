import sqlite3
from pathlib import Path
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    db_path = Path("db/alpha_vault.db")
    if not db_path.exists():
        print("Database not found.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Query latest 32 alpha runs with their formula, status and error message
        cursor.execute("""
            SELECT id, formula, status, sharpe, fitness, turnover, error_message, family
            FROM alpha_runs
            ORDER BY id DESC
            LIMIT 32
        """)
        rows = cursor.fetchall()
        print("=============================================================")
        print("LATEST 32 ALPHAS RUN AND THEIR STATUSES:")
        print("=============================================================")
        for r in rows:
            print(f"ID: {r[0]} | Status: {r[2]} | Sharpe: {r[3]} | Family: {r[7]}")
            print(f"  Formula: {r[1]}")
            if r[6]:
                print(f"  Error: {r[6]}")
            print("-" * 60)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()

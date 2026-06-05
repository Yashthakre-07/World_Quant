import sqlite3
import os

db_path = "c:/Users/Admin/Documents/VIBE_YT/wq/db/alpha_vault.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Search for formulas containing 'anl' with status in ('HARD_REJECT', 'SOFT_FAIL')
        # These are compiled successfully because they didn't throw ERROR.
        cursor.execute("""
            SELECT id, family, formula, status, sharpe, fitness, error_message 
            FROM alpha_runs 
            WHERE formula LIKE '%anl%' AND status IN ('HARD_REJECT', 'SOFT_FAIL')
            ORDER BY id DESC
            LIMIT 50;
        """)
        rows = cursor.fetchall()
        print(f"Total compiled-successfully 'anl' alphas found: {len(rows)}")
        for r in rows:
            print(f"ID: {r[0]} | Status: {r[3]} | Sharpe: {r[4]} | Fitness: {r[5]}")
            print(f"Formula: {r[2]}")
            print(f"Error Msg: {r[6]}")
            print("-" * 60)
    except Exception as e:
        print(f"Database error: {e}")
    conn.close()
else:
    print("Database not found.")

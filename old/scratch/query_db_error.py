import sqlite3
import os

def main():
    db_path = "db/alpha_vault.db"
    if not os.path.exists(db_path):
        print("Database not found.")
        return
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        # Fetch the latest 10 failed runs of GRP_A_ or GRP_B_ families
        cur.execute("""
            SELECT family, formula, status, error_message 
            FROM alpha_runs 
            WHERE (family LIKE 'GRP_A_%' OR family LIKE 'GRP_B_%') 
            ORDER BY id DESC 
            LIMIT 15
        """)
        rows = cur.fetchall()
        print(f"Retrieved {len(rows)} latest runs.")
        for row in rows:
            print(f"Family: {row[0]}")
            print(f"Formula: {row[1]}")
            print(f"Status: {row[2]}")
            print(f"Error Message: {row[3]}")
            print("="*60)
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()

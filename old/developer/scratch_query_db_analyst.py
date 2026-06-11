import sqlite3
from pathlib import Path

def main():
    db_path = Path("db/alpha_vault.db")
    if not db_path.exists():
        # Fallback to alternative paths if any
        db_path = Path("/data/alpha_vault.db")
        if not db_path.exists():
            print("Database not found.")
            return

    print(f"Connecting to database: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cursor.fetchall()]
        print(f"Tables in database: {tables}")
        
        if "alpha_runs" in tables:
            # Let's search for formulas containing analyst fields
            # We can search for 'actual_' or 'est_' or fields like 'eps' or 'analyst'
            cursor.execute("SELECT COUNT(*) FROM alpha_runs WHERE formula LIKE '%est_%' OR formula LIKE '%actual_%' OR formula LIKE '%anl%'")
            count = cursor.fetchone()[0]
            print(f"Number of runs with potential analyst fields: {count}")
            
            cursor.execute("SELECT id, formula, sharpe, fitness, status FROM alpha_runs WHERE formula LIKE '%est_%' OR formula LIKE '%actual_%' OR formula LIKE '%anl%' LIMIT 10")
            rows = cursor.fetchall()
            for r in rows:
                print(f"  ID: {r[0]} | Sharpe: {r[2]} | Fitness: {r[3]} | Status: {r[4]}")
                print(f"    Formula: {r[1][:120]}...")
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()

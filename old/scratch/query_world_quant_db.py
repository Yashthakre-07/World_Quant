import sqlite3

def main():
    db_files = ['db/world_quant.db', 'db/alpha_vault.db']
    
    for db in db_files:
        print(f"\n==================== INSPECTING DB: {db} ====================")
        try:
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            
            # Check all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("Tables:", tables)
            
            for t in tables:
                t_name = t[0]
                cursor.execute(f"SELECT count(*) FROM {t_name}")
                print(f"  Table '{t_name}' row count: {cursor.fetchone()[0]}")
                
                # Check columns
                cursor.execute(f"PRAGMA table_info({t_name})")
                cols = [row[1] for row in cursor.fetchall()]
                print(f"  Columns of '{t_name}': {cols}")
                
                # Sample row if any
                cursor.execute(f"SELECT * FROM {t_name} LIMIT 1")
                sample = cursor.fetchone()
                if sample:
                    print(f"  Sample row from '{t_name}': {sample}")
            conn.close()
        except Exception as e:
            print(f"Error reading {db}: {e}")

if __name__ == "__main__":
    main()

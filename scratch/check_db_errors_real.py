import sqlite3

def check():
    db_paths = ['C:/data/alpha_vault.db', 'db/alpha_vault.db']
    for path in db_paths:
        print(f"=== Database: {path} ===")
        try:
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            # Get the most recent 10 runs with their status
            cursor.execute("SELECT id, family, status, error_message, formula FROM alpha_runs ORDER BY id DESC LIMIT 10")
            rows = cursor.fetchall()
            if not rows:
                print("No runs found in this database.")
            for row in rows:
                print(f"ID: {row[0]} | Family: {row[1]} | Status: {row[2]}")
                print(f"Formula: {row[4]}")
                print(f"Error: {row[3]}")
                print("-" * 50)
            conn.close()
        except Exception as e:
            print(f"Error reading {path}: {e}")

if __name__ == '__main__':
    check()

import sqlite3

def check_more():
    path = 'C:/data/alpha_vault.db'
    print(f"=== Database: {path} ===")
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, family, status, error_message, formula FROM alpha_runs WHERE family LIKE 'GRP_B%' ORDER BY id DESC LIMIT 15")
        rows = cursor.fetchall()
        for row in rows:
            print(f"ID: {row[0]} | Family: {row[1]} | Status: {row[2]}")
            print(f"Formula: {row[4]}")
            print(f"Error: {row[3]}")
            print("-" * 50)
        conn.close()
    except Exception as e:
        print(f"Error reading: {e}")

if __name__ == '__main__':
    check_more()

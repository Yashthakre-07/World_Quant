import sqlite3

def check_latest():
    conn = sqlite3.connect('db/alpha_vault.db')
    cursor = conn.cursor()
    # Let's get the 32 most recent runs in the database
    cursor.execute("SELECT id, family, formula, status, sharpe, fitness, error_message FROM alpha_runs ORDER BY id DESC LIMIT 16")
    for row in cursor.fetchall():
        print(f"ID: {row[0]} | Family: {row[1]} | Status: {row[3]} | Sharpe: {row[4]}")
        print(f"Formula: {row[2]}")
        print(f"Error: {row[6]}")
        print("-" * 50)
    conn.close()

if __name__ == '__main__':
    check_latest()

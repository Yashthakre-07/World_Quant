import sqlite3

def check():
    conn = sqlite3.connect('db/alpha_vault.db')
    cursor = conn.cursor()
    # Let's get the 16 most recent error runs
    cursor.execute("SELECT family, formula, error_message FROM alpha_runs WHERE status = 'ERROR' AND family LIKE 'GRP_B_ELITE_THEME_MUTATION_%' ORDER BY id DESC LIMIT 16")
    for row in cursor.fetchall():
        print(f"Family: {row[0]}")
        print(f"Formula: {row[1]}")
        print(f"Error: {row[2]}")
        print("-" * 50)
    conn.close()

if __name__ == '__main__':
    check()

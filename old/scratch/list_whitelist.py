import sqlite3

def main():
    conn = sqlite3.connect('db/alpha_vault.db')
    cursor = conn.cursor()
    
    # Check what tables exist
    tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    if 'whitelisted_variables' not in tables:
        print("Table 'whitelisted_variables' not found in database.")
        return
        
    rows = cursor.execute("""
        SELECT dataset, variable_id, description 
        FROM whitelisted_variables 
        WHERE dataset IN ('analyst4', 'analyst14', 'analyst16', 'analyst45')
        ORDER BY dataset, variable_id
    """).fetchall()
    
    print("## Whitelisted Fields from Database\n")
    print("| Dataset | Variable ID | Description |")
    print("| --- | --- | --- |")
    for r in rows:
        desc = r[2].replace('\n', ' ').strip()
        if len(desc) > 80:
            desc = desc[:77] + "..."
        print(f"| {r[0]} | `{r[1]}` | {desc} |")
        
    conn.close()

if __name__ == '__main__':
    main()

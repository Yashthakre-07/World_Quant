import sqlite3
import os

db_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\db\alpha_vault.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Total count in the table
    cursor.execute("SELECT COUNT(*) FROM whitelisted_variables")
    total_count = cursor.fetchone()[0]
    print(f"TOTAL_COUNT: {total_count}")
    
    # Group by dataset to see all
    cursor.execute("SELECT dataset, COUNT(*) FROM whitelisted_variables GROUP BY dataset ORDER BY COUNT(*) DESC")
    rows = cursor.fetchall()
    print("\nBreakdown of all whitelisted fields in the database:")
    for row in rows:
        print(f"  {row[0]}: {row[1]} fields")
        
    conn.close()
else:
    print("Database does not exist.")

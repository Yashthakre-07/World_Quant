import sqlite3
import json
import os

db_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\db\alpha_vault.db"
theme_json_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\theme_Dataset.json"

with open(theme_json_path, 'r', encoding='utf-8') as f:
    theme_datasets = json.load(f)
theme_ids = {d['id']: d for d in theme_datasets}

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Let's see table columns
    try:
        cursor.execute("PRAGMA table_info(whitelisted_variables)")
        columns = cursor.fetchall()
        print("Columns in whitelisted_variables:", [c[1] for c in columns])
    except Exception as e:
        print("Error getting table info:", e)
        
    # Query all variables in whitelist table
    try:
        cursor.execute("SELECT dataset, COUNT(*) FROM whitelisted_variables GROUP BY dataset")
        rows = cursor.fetchall()
        print("\nWhitelisted counts by dataset in db/alpha_vault.db:")
        
        db_counts = {}
        for row in rows:
            print(f"  {row[0]}: {row[1]}")
            db_counts[row[0]] = row[1]
            
        print("\nMapping to our 42 Theme Datasets:")
        for ds in theme_datasets:
            ds_id = ds['id']
            # Sometimes the dataset ID stored in DB matches the theme ID, let's look for match
            # Let's check exact match, or case-insensitive, or substring
            count = 0
            for db_ds, db_count in db_counts.items():
                if db_ds.lower() == ds_id.lower() or db_ds.lower().replace('_', '') == ds_id.lower():
                    count = db_count
                    break
            print(f"  {ds_id:15s} ({ds['category']}): {count} whitelisted fields")
            
    except Exception as e:
        print("Error querying counts:", e)
    finally:
        conn.close()
else:
    print(f"Database {db_path} does not exist.")

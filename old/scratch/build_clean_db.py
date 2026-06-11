import sqlite3
import json
import os

DB_PATH = "db/alpha_vault.db"
FIELDS_DIR = "scratch/selected_analyst_fields"

def init_clean_db():
    print(f"[*] Initializing clean database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create a table for whitelist variables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS whitelisted_variables (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset         TEXT NOT NULL,
        variable_id     TEXT NOT NULL UNIQUE,
        description     TEXT,
        updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

def populate_whitelist():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    total_added = 0
    for file_name in os.listdir(FIELDS_DIR):
        if file_name.endswith("_fields.json"):
            dataset_name = file_name.replace("_fields.json", "")
            file_path = os.path.join(FIELDS_DIR, file_name)
            
            print(f"[*] Parsing active whitelist file: {file_name} ...")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    fields = json.load(f)
                
                for field in fields:
                    var_id = field.get("id")
                    desc = field.get("description", "")
                    if var_id:
                        cursor.execute("""
                            INSERT INTO whitelisted_variables (dataset, variable_id, description)
                            VALUES (?, ?, ?)
                            ON CONFLICT(variable_id) DO UPDATE SET
                                description = excluded.description,
                                updated_at = CURRENT_TIMESTAMP
                        """, (dataset_name, var_id, desc))
                        total_added += 1
            except Exception as e:
                print(f"  [-] Failed to parse {file_name}: {e}")
                
    conn.commit()
    conn.close()
    print(f"[SUCCESS] Database synced. Logged exactly {total_added} whitelisted active fields into your database.")

if __name__ == "__main__":
    init_clean_db()
    populate_whitelist()

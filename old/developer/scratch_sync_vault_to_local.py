import os
import sqlite3
import json
import urllib.request
import ssl
from pathlib import Path

# Disable SSL verification issues if any
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SERVERS = {
    "Local Group A Server": {
        "url": "http://localhost:8000",
        "token": "yashthakreop"
    },
    "Local Group B Server": {
        "url": "http://localhost:8000",
        "token": "yashthakrepro"
    }
}

DB_PATH = "db/alpha_vault.db"
ALPHAS_DIR = Path("alphas")
ALPHAS_DIR.mkdir(exist_ok=True)

def query_stats(server_url):
    url = f"{server_url.rstrip('/')}/api/stats"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=45) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body), response.status
    except Exception as e:
        return {"error": str(e)}, 500

def main():
    print("=" * 60)
    print("STARTING DUAL-SERVER VAULT SYNC TO LOCAL MACHINE")
    print("=" * 60)
    
    # Initialize connection to local database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure tables exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alpha_runs (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id          TEXT NOT NULL,
        timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
        family          TEXT NOT NULL,
        hypothesis      TEXT,
        formula         TEXT NOT NULL,
        region          TEXT DEFAULT 'USA',
        universe        TEXT DEFAULT 'TOP3000',
        neutralization  TEXT DEFAULT 'SUBINDUSTRY',
        decay           INTEGER DEFAULT 6,
        truncation      REAL DEFAULT 0.1,
        delay           INTEGER DEFAULT 1,
        sharpe          REAL,
        fitness         REAL,
        turnover        REAL,
        checks_passed   INTEGER DEFAULT 0,
        weight_check    TEXT,
        sub_sharpe      REAL,
        status          TEXT NOT NULL,
        alpha_link      TEXT,
        sim_link        TEXT,
        error_message   TEXT,
        llm_model       TEXT,
        parent_id       INTEGER
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS submitted_alphas (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        alpha_run_id    INTEGER NOT NULL,
        alpha_id        TEXT NOT NULL,
        submitted_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
        self_corr_pass  BOOLEAN,
        os_sharpe       REAL,
        FOREIGN KEY (alpha_run_id) REFERENCES alpha_runs(id)
    );
    """)
    conn.commit()
    
    total_added_db = 0
    total_added_json = 0
    total_skipped = 0
    
    for name, config in SERVERS.items():
        print(f"\nFetching stats from {name}...")
        data, status = query_stats(config["url"])
        
        if status != 200:
            print(f"  [ERROR] Failed to fetch stats: {data.get('error')}")
            continue
            
        vault_alphas = data.get("vault_alphas", [])
        print(f"  Found {len(vault_alphas)} alphas in the remote vault.")
        
        for a in vault_alphas:
            alpha_id = a.get("alpha_id")
            formula = a.get("formula")
            status_val = a.get("status")
            sharpe = a.get("sharpe")
            fitness = a.get("fitness")
            turnover = a.get("turnover")
            family = a.get("family", "Unknown")
            error_message = a.get("error_message", "")
            alpha_link = a.get("alpha_link", "#")
            created_at = a.get("created_at", "")
            
            if not alpha_id or not formula:
                continue
                
            # Check if this alpha is already in the database
            cursor.execute("SELECT id FROM alpha_runs WHERE run_id = ? OR formula = ?", (alpha_id, formula))
            db_row = cursor.fetchone()
            
            local_run_id = None
            if not db_row:
                # Insert into local database
                # Default hypothesis
                hypothesis = f"Synced from remote vault {name}. ID: {alpha_id}"
                cursor.execute("""
                INSERT INTO alpha_runs (
                    run_id, family, hypothesis, formula, region, universe, neutralization,
                    decay, truncation, delay, sharpe, fitness, turnover, checks_passed,
                    weight_check, sub_sharpe, status, alpha_link, sim_link, error_message,
                    llm_model
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alpha_id, family, hypothesis, formula, "USA", "TOP3000", "SUBINDUSTRY",
                    6, 0.1, 1, sharpe, fitness, turnover, 0, "PASS", -1.0, status_val,
                    alpha_link, "#", error_message, "synced"
                ))
                local_run_id = cursor.lastrowid
                total_added_db += 1
            else:
                local_run_id = db_row[0]
                
            # If submitted, ensure record in submitted_alphas
            if status_val == "SUBMITTED":
                cursor.execute("SELECT id FROM submitted_alphas WHERE alpha_id = ? OR alpha_run_id = ?", (alpha_id, local_run_id))
                sub_row = cursor.fetchone()
                if not sub_row:
                    cursor.execute("""
                    INSERT INTO submitted_alphas (alpha_run_id, alpha_id, self_corr_pass)
                    VALUES (?, ?, ?)
                    """, (local_run_id, alpha_id, True))
                    
            # Save local JSON file if not exists
            json_file = ALPHAS_DIR / f"alpha_{alpha_id}.json"
            if not json_file.exists():
                json_data = {
                    "alpha_id": alpha_id,
                    "family": family,
                    "formula": formula,
                    "sharpe": sharpe,
                    "fitness": fitness,
                    "turnover": turnover,
                    "status": status_val,
                    "error_message": error_message,
                    "alpha_link": alpha_link,
                    "created_at": created_at
                }
                with open(json_file, "w") as jf:
                    json.dump(json_data, jf, indent=2)
                total_added_json += 1
            else:
                total_skipped += 1
                
        conn.commit()
        print(f"  Completed sync for {name}.")
        
    # Get new local totals
    cursor.execute("SELECT COUNT(*) FROM alpha_runs")
    total_db_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM alpha_runs WHERE status = 'SUBMITTED'")
    total_sub_count = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("* SYNC COMPLETE *")
    print("=" * 60)
    print(f"New Alphas Added to Database: {total_added_db}")
    print(f"New JSON Files Saved: {total_added_json}")
    print(f"Total Local Alphas in DB: {total_db_count} (Submissions: {total_sub_count})")
    print(f"Total JSON Files in Directory: {len(list(ALPHAS_DIR.glob('alpha_*.json')))}")
    print("=" * 60)

if __name__ == "__main__":
    main()

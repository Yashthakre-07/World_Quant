import sqlite3
import os
import re

# 1. Search the SQLite database for any runs with analyst fields that completed
db_path = "c:/Users/Admin/Documents/VIBE_YT/wq/db/alpha_vault.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT formula, status, sharpe, fitness, error_message FROM alpha_runs WHERE formula LIKE '%anl%' AND status != 'ERROR' LIMIT 30;")
        rows = cursor.fetchall()
        print(f"Database runs containing 'anl' that didn't get ERROR: {len(rows)}")
        for r in rows:
            print(f"Formula: {r[0]}")
            print(f"Status: {r[1]} | Sharpe: {r[2]} | Fitness: {r[3]} | Error: {r[4]}")
            print("-" * 50)
    except Exception as e:
        print(f"Database error: {e}")
    conn.close()

# 2. Search all python files in the workspace for any analyst formula strings
print("\nSearching python files in workspace for compliant analyst formulas...")
pattern = re.compile(r'"[^"]*anl[^"]*"|\'[^\']*anl[^\']*\n')
for root, dirs, files in os.walk("c:/Users/Admin/Documents/VIBE_YT/wq"):
    for file in files:
        if file.endswith(".py") and file != "search_successful_analyst_alphas.py":
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if "anl" in content.lower():
                        # Find lines containing formulas with anl
                        for line_idx, line in enumerate(content.split("\n"), 1):
                            if "anl" in line and ("formula" in line or "regular" in line or "trade_when" in line):
                                print(f"File: {file} (L{line_idx}): {line.strip()[:120]}")
            except Exception as e:
                pass

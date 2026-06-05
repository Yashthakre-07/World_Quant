import sqlite3
import os

def analyze_db():
    db_path = "db/alpha_vault.db"
    if not os.path.exists(db_path):
        print("Database not found.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Total statistics
    total = cursor.execute("SELECT COUNT(*) FROM alpha_runs").fetchone()[0]
    by_status = cursor.execute("SELECT status, COUNT(*), AVG(sharpe), AVG(fitness) FROM alpha_runs GROUP BY status").fetchall()
    
    print("=== SUMMARY BY STATUS ===")
    print(f"Total Runs: {total}")
    for status, count, avg_sharpe, avg_fitness in by_status:
        print(f"  {status:12s}: Count={count:3d} | Avg Sharpe={avg_sharpe if avg_sharpe else 0:.4f} | Avg Fitness={avg_fitness if avg_fitness else 0:.4f}")
        
    # 2. Analyze TOP 20 highest Sharpe alphas
    print("\n=== TOP 15 HIGHEST SHARPE ALPHAS ===")
    top_sharpe = cursor.execute("""
        SELECT id, formula, sharpe, fitness, turnover, status, error_message 
        FROM alpha_runs 
        WHERE status != 'ERROR' 
        ORDER BY sharpe DESC 
        LIMIT 15
    """).fetchall()
    for idx, r in enumerate(top_sharpe, 1):
        print(f"{idx:2d}. ID={r[0]} | Sharpe={r[2]:.4f} | Fitness={r[3]:.4f} | Turnover={r[4]:.2f}% | Status={r[5]}")
        print(f"    Formula: {r[1]}")
        
    # 3. Analyze what datasets are used in successful (SUBMITTED or SOFT_FAIL with Sharpe > 1.25)
    print("\n=== DATASET PERFORMANCE ANALYSIS ===")
    # We classify datasets based on keywords in formula
    datasets = {
        "price_volume": "formula NOT LIKE '%anl%' AND formula NOT LIKE '%securities%' AND formula NOT LIKE '%liabilities%' AND formula NOT LIKE '%depreciation%' AND formula NOT LIKE '%asset%' AND formula NOT LIKE '%expense%'",
        "analyst": "(formula LIKE '%anl%' OR formula LIKE '%eps_estimate%' OR formula LIKE '%sales_estimate%')",
        "fundamental": "(formula LIKE '%securities%' OR formula LIKE '%liabilities%' OR formula LIKE '%depreciation%' OR formula LIKE '%asset%' OR formula LIKE '%expense%' OR formula LIKE '%return_on_pension%')"
    }
    
    for name, condition in datasets.items():
        count = cursor.execute(f"SELECT COUNT(*) FROM alpha_runs WHERE {condition}").fetchone()[0]
        avg_s = cursor.execute(f"SELECT AVG(sharpe) FROM alpha_runs WHERE {condition} AND status != 'ERROR'").fetchone()[0]
        max_s = cursor.execute(f"SELECT MAX(sharpe) FROM alpha_runs WHERE {condition} AND status != 'ERROR'").fetchone()[0]
        success = cursor.execute(f"SELECT COUNT(*) FROM alpha_runs WHERE {condition} AND status = 'SUBMITTED'").fetchone()[0]
        soft_fail = cursor.execute(f"SELECT COUNT(*) FROM alpha_runs WHERE {condition} AND status = 'SOFT_FAIL'").fetchone()[0]
        print(f"Dataset Group: {name:15s} | Count={count:3d} | Avg Sharpe={avg_s if avg_s else 0:.4f} | Max Sharpe={max_s if max_s else 0:.4f} | Submitted={success} | Soft Fail={soft_fail}")

    # 4. Check if there are any error patterns in WQ responses
    print("\n=== TYPICAL COMPILER OR SIMULATION ERRORS ===")
    errors = cursor.execute("""
        SELECT error_message, COUNT(*) 
        FROM alpha_runs 
        WHERE error_message IS NOT NULL AND error_message != ''
        GROUP BY error_message
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """).fetchall()
    for err, count in errors:
        print(f"  [{count:2d} times] {err[:120]}")
        
    conn.close()

if __name__ == "__main__":
    analyze_db()

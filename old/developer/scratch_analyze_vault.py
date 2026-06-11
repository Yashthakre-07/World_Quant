import sqlite3
import pandas as pd

DB_PATH = "db/alpha_vault.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    
    print("=" * 60)
    print("ANALYZING LOCAL ALPHA VAULT")
    print("=" * 60)
    
    # 1. Total runs and counts by status
    df_status = pd.read_sql_query("SELECT status, COUNT(*) as count FROM alpha_runs GROUP BY status", conn)
    print("\n--- Alpha Count by Status ---")
    print(df_status)
    
    # 2. Top-performing families (highest average Sharpe / Fitness or most SUBMITTED)
    df_family = pd.read_sql_query("""
        SELECT family, 
               COUNT(*) as total_runs,
               SUM(CASE WHEN status='SUBMITTED' THEN 1 ELSE 0 END) as submitted_count,
               AVG(sharpe) as avg_sharpe,
               MAX(sharpe) as max_sharpe,
               AVG(fitness) as avg_fitness,
               MAX(fitness) as max_fitness
        FROM alpha_runs 
        GROUP BY family 
        ORDER BY submitted_count DESC, max_sharpe DESC
    """, conn)
    print("\n--- Family Performance Statistics ---")
    print(df_family.head(20))
    
    # 3. Sample of successfully submitted alphas (status = 'SUBMITTED')
    df_submitted = pd.read_sql_query("""
        SELECT family, formula, sharpe, fitness, turnover 
        FROM alpha_runs 
        WHERE status='SUBMITTED' 
        ORDER BY sharpe DESC 
        LIMIT 10
    """, conn)
    print("\n--- Sample of Successfully SUBMITTED Alphas ---")
    for idx, row in df_submitted.iterrows():
        print(f"\n[{row['family']}] Sharpe: {row['sharpe']:.2f}, Fitness: {row['fitness']:.2f}, Turnover: {row['turnover']:.1f}%")
        print(f"Formula: {row['formula']}")
        
    # 4. Sample of failed/rejected alphas (status = 'HARD_REJECT' or 'SOFT_FAIL')
    df_failed = pd.read_sql_query("""
        SELECT family, formula, status, error_message 
        FROM alpha_runs 
        WHERE status IN ('HARD_REJECT', 'SOFT_FAIL') 
        LIMIT 5
    """, conn)
    print("\n--- Sample of Failed/Rejected Alphas ---")
    for idx, row in df_failed.iterrows():
        print(f"\n[{row['family']}] Status: {row['status']}")
        print(f"Formula: {row['formula']}")
        print(f"Error: {row['error_message']}")
        
    conn.close()

if __name__ == "__main__":
    main()

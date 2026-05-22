import sqlite3
from src.config import DB_PATH
from src.logger import agent_logger

_db_initialized = False

def init_db():
    global _db_initialized
    if _db_initialized:
        return
    _db_initialized = True
    agent_logger.info(f"[DATABASE] Initializing database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table for all simulation runs
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
        parent_id       INTEGER,
        FOREIGN KEY (parent_id) REFERENCES alpha_runs(id)
    );
    """)

    # Create table for successful submissions
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

    # Create family stats view if not exists
    cursor.execute("""
    DROP VIEW IF EXISTS family_stats;
    """)
    cursor.execute("""
    CREATE VIEW family_stats AS
    SELECT
        family,
        COUNT(*) as total_runs,
        SUM(CASE WHEN status = 'SUBMITTED' THEN 1 ELSE 0 END) as submitted,
        AVG(CASE WHEN sharpe IS NOT NULL THEN sharpe END) as avg_sharpe,
        MAX(sharpe) as best_sharpe,
        AVG(CASE WHEN fitness IS NOT NULL THEN fitness END) as avg_fitness,
        ROUND(100.0 * SUM(CASE WHEN status = 'SUBMITTED' THEN 1 ELSE 0 END) / COUNT(*), 1) as success_rate
    FROM alpha_runs
    GROUP BY family;
    """)

    conn.commit()
    conn.close()
    agent_logger.info("[DATABASE] Database successfully initialized.")

def save_alpha_run(run_data: dict) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
    INSERT INTO alpha_runs (
        run_id, family, hypothesis, formula, region, universe, neutralization,
        decay, truncation, delay, sharpe, fitness, turnover, checks_passed,
        weight_check, sub_sharpe, status, alpha_link, sim_link, error_message,
        llm_model, parent_id
    ) VALUES (
        :run_id, :family, :hypothesis, :formula, :region, :universe, :neutralization,
        :decay, :truncation, :delay, :sharpe, :fitness, :turnover, :checks_passed,
        :weight_check, :sub_sharpe, :status, :alpha_link, :sim_link, :error_message,
        :llm_model, :parent_id
    )
    """
    
    cursor.execute(query, run_data)
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id

def save_submitted_alpha(alpha_run_id: int, alpha_id: str, self_corr_pass: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO submitted_alphas (alpha_run_id, alpha_id, self_corr_pass)
    VALUES (?, ?, ?)
    """, (alpha_run_id, alpha_id, self_corr_pass))
    conn.commit()
    conn.close()

def get_learning_history(family: str, limit: int = 5):
    """
    Retrieves high-performing (Sharpe > 1.25) and failed (Sharpe < 1.0 or STATUS = 'ERROR')
    formulas for the given family to include in the LLM prompt.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Successes (Sharpe descending)
    cursor.execute("""
    SELECT formula, sharpe, fitness, turnover FROM alpha_runs
    WHERE family = ? AND status = 'SUBMITTED'
    ORDER BY sharpe DESC LIMIT ?
    """, (family, limit))
    successes = cursor.fetchall()

    # Failures (Sharpe ascending or status = ERROR)
    cursor.execute("""
    SELECT formula, sharpe, fitness, turnover, error_message FROM alpha_runs
    WHERE family = ? AND (status = 'HARD_REJECT' OR status = 'ERROR')
    ORDER BY id DESC LIMIT ?
    """, (family, limit))
    failures = cursor.fetchall()

    conn.close()
    return successes, failures

def get_stats_summary():
    """
    Returns general stats for active status monitoring.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM alpha_runs")
    total_runs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM alpha_runs WHERE status = 'SUBMITTED'")
    total_submissions = cursor.fetchone()[0]

    cursor.execute("SELECT MAX(sharpe) FROM alpha_runs")
    best_sharpe = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT MAX(fitness) FROM alpha_runs")
    best_fitness = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT family, total_runs, submitted, success_rate FROM family_stats")
    families = cursor.fetchall()

    conn.close()
    return {
        "total_runs": total_runs,
        "total_submissions": total_submissions,
        "best_sharpe": round(best_sharpe, 3),
        "best_fitness": round(best_fitness, 3),
        "families": [
            {"family": f[0], "total_runs": f[1], "submitted": f[2], "success_rate": f[3]} for f in families
        ]
    }

def check_already_simulated(formula: str) -> dict:
    """Check if the alpha formula has already completed simulation to skip repeat simulations."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT status, sharpe, fitness, turnover, error_message, alpha_link, sim_link
    FROM alpha_runs
    WHERE formula = ? AND status IN ('SUBMITTED', 'HARD_REJECT', 'SOFT_FAIL')
    ORDER BY id DESC LIMIT 1
    """, (formula,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "status": row[0],
            "sharpe": row[1],
            "fitness": row[2],
            "turnover": row[3],
            "error_message": row[4],
            "alpha_link": row[5],
            "sim_link": row[6]
        }
    return None


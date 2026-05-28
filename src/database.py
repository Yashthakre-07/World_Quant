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

    # Create tables for automation platform
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS all_alphas (
        alpha_id        TEXT PRIMARY KEY,
        formula         TEXT,
        sharpe          REAL,
        fitness         REAL,
        turnover        REAL,
        status          TEXT DEFAULT 'GRAY',
        yellow_flag     INTEGER DEFAULT 0,
        retry_count     INTEGER DEFAULT 0,
        last_attempt    DATETIME,
        updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rejected_alphas (
        alpha_id        TEXT PRIMARY KEY,
        rejected_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
        reason          TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS queue (
        alpha_id        TEXT PRIMARY KEY,
        added_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
        status          TEXT DEFAULT 'PENDING'
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
    # Update all_alphas status to GREEN
    cursor.execute("""
    INSERT INTO all_alphas (alpha_id, status, yellow_flag, updated_at)
    VALUES (?, 'GREEN', 0, CURRENT_TIMESTAMP)
    ON CONFLICT(alpha_id) DO UPDATE SET
        status = 'GREEN',
        yellow_flag = 0,
        updated_at = CURRENT_TIMESTAMP
    """, (alpha_id,))
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


def upsert_all_alphas(alphas_list: list):
    """
    Inserts or updates a list of alphas fetched from WQ.
    Respects existing GREEN (submitted) and YELLOW (rejected) statuses.
    Each alpha in the list is a dict with keys: alpha_id, formula, sharpe, fitness, turnover.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch existing yellow and green IDs to respect status logic
    cursor.execute("SELECT alpha_id FROM rejected_alphas")
    yellow_ids = {row[0] for row in cursor.fetchall()}
    
    cursor.execute("SELECT alpha_id FROM submitted_alphas")
    green_ids = {row[0] for row in cursor.fetchall()}
    
    for alpha in alphas_list:
        alpha_id = alpha["alpha_id"]
        formula = alpha["formula"]
        sharpe = alpha["sharpe"]
        fitness = alpha["fitness"]
        turnover = alpha["turnover"]
        
        # Determine status and yellow flag based on persistent tables
        if alpha_id in green_ids:
            status = 'GREEN'
            yellow_flag = 0
        elif alpha_id in yellow_ids:
            status = 'YELLOW'
            yellow_flag = 1
        else:
            status = 'GRAY'
            yellow_flag = 0
            
        cursor.execute("""
        INSERT INTO all_alphas (alpha_id, formula, sharpe, fitness, turnover, status, yellow_flag)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(alpha_id) DO UPDATE SET
            formula = COALESCE(excluded.formula, formula),
            sharpe = COALESCE(excluded.sharpe, sharpe),
            fitness = COALESCE(excluded.fitness, fitness),
            turnover = COALESCE(excluded.turnover, turnover),
            status = CASE 
                WHEN all_alphas.status IN ('GREEN', 'YELLOW') THEN all_alphas.status 
                ELSE excluded.status 
            END,
            yellow_flag = CASE 
                WHEN all_alphas.yellow_flag = 1 THEN 1 
                ELSE excluded.yellow_flag 
            END,
            updated_at = CURRENT_TIMESTAMP
        """, (alpha_id, formula, sharpe, fitness, turnover, status, yellow_flag))
        
    conn.commit()
    conn.close()

def get_queue_alphas() -> list:
    """
    Returns all alphas currently in the queue joined with their metrics from all_alphas.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.alpha_id, a.formula, a.sharpe, a.fitness, a.turnover, a.status, a.yellow_flag, a.retry_count, q.added_at
        FROM queue q
        LEFT JOIN all_alphas a ON q.alpha_id = a.alpha_id
        ORDER BY q.added_at ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    queue_list = []
    for r in rows:
        queue_list.append({
            "alpha_id": r[0],
            "formula": r[1] or "",
            "sharpe": r[2] or 0.0,
            "fitness": r[3] or 0.0,
            "turnover": r[4] or 0.0,
            "status": r[5] or "GRAY",
            "yellow_flag": bool(r[6]),
            "retry_count": r[7] or 0,
            "added_at": r[8]
        })
    return queue_list

def add_to_queue(alpha_ids: list):
    """
    Adds a list of alpha IDs to the queue table.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for alpha_id in alpha_ids:
        cursor.execute("""
            INSERT INTO queue (alpha_id) 
            VALUES (?)
            ON CONFLICT(alpha_id) DO NOTHING
        """, (alpha_id,))
    conn.commit()
    conn.close()

def remove_from_queue(alpha_ids: list):
    """
    Removes a list of alpha IDs from the queue table.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for alpha_id in alpha_ids:
        cursor.execute("DELETE FROM queue WHERE alpha_id = ?", (alpha_id,))
    conn.commit()
    conn.close()

def clear_queue():
    """
    Clears all entries from the queue table.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM queue")
    conn.commit()
    conn.close()

def mark_alpha_green(alpha_id: str):
    """
    Marks status as GREEN (submitted) in all_alphas, removes from queue,
    and inserts into submitted_alphas if not present.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Update all_alphas
    cursor.execute("""
        INSERT INTO all_alphas (alpha_id, status, yellow_flag, updated_at)
        VALUES (?, 'GREEN', 0, CURRENT_TIMESTAMP)
        ON CONFLICT(alpha_id) DO UPDATE SET
            status = 'GREEN',
            yellow_flag = 0,
            updated_at = CURRENT_TIMESTAMP
    """, (alpha_id,))
    
    # 2. Insert into submitted_alphas if not present (we insert dummy alpha_run_id as -1 since it's a direct platform alpha)
    cursor.execute("SELECT 1 FROM submitted_alphas WHERE alpha_id = ?", (alpha_id,))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO submitted_alphas (alpha_run_id, alpha_id)
            VALUES (-1, ?)
        """, (alpha_id,))
        
    # 3. Remove from queue
    cursor.execute("DELETE FROM queue WHERE alpha_id = ?", (alpha_id,))
    
    conn.commit()
    conn.close()

def mark_alpha_yellow(alpha_id: str, reason: str = ''):
    """
    Marks status as YELLOW (non-submittable) in all_alphas, yellow_flag = 1,
    removes from queue, and inserts into rejected_alphas.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Update all_alphas
    cursor.execute("""
        INSERT INTO all_alphas (alpha_id, status, yellow_flag, updated_at)
        VALUES (?, 'YELLOW', 1, CURRENT_TIMESTAMP)
        ON CONFLICT(alpha_id) DO UPDATE SET
            status = 'YELLOW',
            yellow_flag = 1,
            updated_at = CURRENT_TIMESTAMP
    """, (alpha_id,))
    
    # 2. Insert into rejected_alphas
    cursor.execute("""
        INSERT INTO rejected_alphas (alpha_id, reason)
        VALUES (?, ?)
        ON CONFLICT(alpha_id) DO UPDATE SET
            reason = excluded.reason
    """, (alpha_id, reason))
    
    # 3. Remove from queue
    cursor.execute("DELETE FROM queue WHERE alpha_id = ?", (alpha_id,))
    
    conn.commit()
    conn.close()

def mark_alpha_red(alpha_id: str):
    """
    Marks status as RED (failed, retry pending) in all_alphas, and increments retry_count.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO all_alphas (alpha_id, status, retry_count, last_attempt, updated_at)
        VALUES (?, 'RED', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT(alpha_id) DO UPDATE SET
            status = 'RED',
            retry_count = retry_count + 1,
            last_attempt = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
    """, (alpha_id,))
    conn.commit()
    conn.close()

def get_failed_yellow_alphas() -> list:
    """
    Returns all alphas that are marked as yellow.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.alpha_id, a.formula, a.sharpe, a.fitness, a.turnover, r.rejected_at, r.reason
        FROM rejected_alphas r
        JOIN all_alphas a ON r.alpha_id = a.alpha_id
        ORDER BY r.rejected_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    alphas = []
    for r in rows:
        alphas.append({
            "alpha_id": r[0],
            "formula": r[1] or "",
            "sharpe": r[2] or 0.0,
            "fitness": r[3] or 0.0,
            "turnover": r[4] or 0.0,
            "rejected_at": r[5],
            "reason": r[6] or ""
        })
    return alphas

def get_submitted_green_alphas() -> list:
    """
    Returns all alphas that are marked as green.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.alpha_id, a.formula, a.sharpe, a.fitness, a.turnover, s.submitted_at
        FROM submitted_alphas s
        JOIN all_alphas a ON s.alpha_id = a.alpha_id
        ORDER BY s.submitted_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    alphas = []
    for r in rows:
        alphas.append({
            "alpha_id": r[0],
            "formula": r[1] or "",
            "sharpe": r[2] or 0.0,
            "fitness": r[3] or 0.0,
            "turnover": r[4] or 0.0,
            "submitted_at": r[5]
        })
    return alphas



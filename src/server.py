import json
import sqlite3
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from src.config import DB_PATH, SERVER_HOST, SERVER_PORT
from src.logger import log_broadcast, state_broadcast, agent_logger, update_agent_status

app = FastAPI(title="AlphaForge Console API")

# Serve dashboard static assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Forward root requests to dashboard HTML
@app.get("/")
def read_root():
    return FileResponse("static/index.html")

# Global reference to orchestrator task
orchestrator_task = None
orchestrator_loop_ref = None

@app.get("/api/logs/stream")
async def logs_stream(request: Request):
    """
    SSE stream endpoint broadcasting system logs.
    """
    q = log_broadcast.subscribe()
    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    # Wait for log line, timeout periodically to yield ping keepalive
                    log_entry = await asyncio.wait_for(q.get(), timeout=2.0)
                    yield {
                        "event": "message",
                        "data": json.dumps(log_entry)
                    }
                except asyncio.TimeoutError:
                    yield {
                        "event": "ping",
                        "data": ""
                    }
        finally:
            log_broadcast.unsubscribe(q)
    return EventSourceResponse(event_generator())

@app.get("/api/state/stream")
async def state_stream(request: Request):
    """
    SSE stream endpoint broadcasting agent status pulses.
    """
    q = state_broadcast.subscribe()
    async def event_generator():
        try:
            # Yield initial status on load
            yield {
                "event": "message",
                "data": json.dumps({"status": "AGENT ACTIVE" if orchestrator_task else "AGENT INACTIVE"})
            }
            while True:
                if await request.is_disconnected():
                    break
                try:
                    state_entry = await asyncio.wait_for(q.get(), timeout=2.0)
                    yield {
                        "event": "message",
                        "data": json.dumps(state_entry)
                    }
                except asyncio.TimeoutError:
                    yield {
                        "event": "ping",
                        "data": ""
                    }
        finally:
            state_broadcast.unsubscribe(q)
    return EventSourceResponse(event_generator())

@app.get("/api/stats")
def get_stats():
    """
    Queries current database statistics to populate dashboard tables.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Totals
        cursor.execute("SELECT COUNT(*) FROM alpha_runs")
        total_runs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM alpha_runs WHERE status = 'SUBMITTED'")
        total_submissions = cursor.fetchone()[0]

        cursor.execute("SELECT MAX(sharpe) FROM alpha_runs")
        best_sharpe = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT MAX(fitness) FROM alpha_runs")
        best_fitness = cursor.fetchone()[0] or 0.0

        # Family stats
        cursor.execute("SELECT family, total_runs, submitted, success_rate FROM family_stats")
        families = [
            {"family": f[0], "total_runs": f[1], "submitted": f[2], "success_rate": f[3]} 
            for f in cursor.fetchall()
        ]

        # Recent submissions registry
        cursor.execute("""
            SELECT r.alpha_link, s.alpha_id, r.sharpe, r.fitness, r.turnover 
            FROM submitted_alphas s
            JOIN alpha_runs r ON s.alpha_run_id = r.id
            ORDER BY s.id DESC LIMIT 10
        """)
        submitted_list = [
            {"alpha_link": r[0], "alpha_id": r[1], "sharpe": r[2], "fitness": r[3], "turnover": r[4]}
            for r in cursor.fetchall()
        ]

        conn.close()
        return {
            "total_runs": total_runs,
            "total_submissions": total_submissions,
            "best_sharpe": round(best_sharpe, 3),
            "best_fitness": round(best_fitness, 3),
            "families": families,
            "submitted_list": submitted_list
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/agent/start")
async def start_agent():
    """
    Triggers execution loop tasks.
    """
    global orchestrator_task, orchestrator_loop_ref
    if orchestrator_task:
        return {"status": "error", "message": "Agent is already running."}

    agent_logger.info("[SYSTEM] Booting AlphaForge Orchestration Task...")
    
    # Import locally to avoid circular dependencies
    from src.orchestrator import AlphaOrchestrator
    orchestrator = AlphaOrchestrator()
    orchestrator_loop_ref = orchestrator

    # Run loop as a background async task
    loop = asyncio.get_running_loop()
    orchestrator_task = loop.run_in_executor(None, orchestrator.run_loop)
    
    update_agent_status("AGENT RUNNING")
    return {"status": "success", "message": "Orchestrator started."}

@app.post("/api/agent/stop")
async def stop_agent():
    """
    Signals active execution loop to safely shut down.
    """
    global orchestrator_task, orchestrator_loop_ref
    if not orchestrator_task:
        return {"status": "error", "message": "Agent is not running."}

    agent_logger.info("[SYSTEM] Shutdown signal received. Requesting orchestration loop stop...")
    if orchestrator_loop_ref:
        orchestrator_loop_ref.stop()
    
    orchestrator_task = None
    orchestrator_loop_ref = None
    update_agent_status("AGENT INACTIVE")
    return {"status": "success", "message": "Orchestrator stopped."}

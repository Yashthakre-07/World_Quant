import os
import sys
import json
import time
import uuid
import random
import base64
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify, render_template_string, request

# Add parent directory to path to allow importing from src
sys.path.append(str(Path(__file__).resolve().parent))

from src.auth import WQSession
from src.database import init_db, save_alpha_run, save_submitted_alpha, check_already_simulated
from src.evaluator import evaluate_alpha_metrics
from src.config import WQ_SIM_URL, WQ_ALPHAS_URL, DEFAULT_SIM_SETTINGS, ALPHAS_OUT_DIR, MAX_CONCURRENT_SIMS

# Initialize Flask app
app = Flask(__name__)

# Secure API token for the /api/queue-alpha push endpoint
# Set API_SECRET_TOKEN in Render environment variables
API_SECRET_TOKEN = os.environ.get("API_SECRET_TOKEN", "wq-default-token-change-me")

# Lock to space API submissions sequentially and avoid rate limits
submission_lock = threading.Lock()

# Shared Pipeline State
pipeline_state = {
    "status": "RUNNING",  # RUNNING, COMPLETED
    "alphas": [],
    "logs": []
}

def log_message(level, msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] [{level}] {msg}"
    print(full_msg)
    pipeline_state["logs"].append(full_msg)

# HTML Dashboard Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AlphaForge Pipeline Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #08090d;
            --card-bg: rgba(18, 22, 33, 0.55);
            --border-color: rgba(255, 255, 255, 0.04);
            --border-glow: rgba(0, 242, 254, 0.12);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-teal: #00f2fe;
            --accent-blue: #4facfe;
            --color-success: #00e676;
            --color-warning: #ffd600;
            --color-danger: #ff1744;
            --color-info: #00b0ff;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--accent-teal), var(--accent-blue), var(--color-success), var(--color-warning), var(--color-danger));
            z-index: 1000;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 10% 10%, rgba(0, 242, 254, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 90% 90%, rgba(79, 172, 254, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 50% 50%, rgba(0, 230, 118, 0.01) 0%, transparent 60%);
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 40px;
            border-bottom: 1px solid var(--border-color);
            backdrop-filter: blur(20px);
            background-color: rgba(8, 9, 13, 0.8);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .logo {
            font-size: 26px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--accent-teal), var(--accent-blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo::before {
            content: '';
            display: inline-block;
            width: 12px;
            height: 12px;
            background: linear-gradient(135deg, var(--accent-teal), var(--accent-blue));
            border-radius: 50%;
            box-shadow: 0 0 16px var(--accent-teal);
        }

        .pipeline-status-badge {
            font-size: 12px;
            font-weight: 700;
            padding: 6px 16px;
            border-radius: 30px;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 8px;
            border: 1px solid transparent;
            text-transform: uppercase;
        }

        .pipeline-status-badge.running {
            background-color: rgba(0, 176, 255, 0.06);
            color: var(--color-info);
            border-color: rgba(0, 176, 255, 0.2);
            box-shadow: 0 0 15px rgba(0, 176, 255, 0.08);
        }

        .pipeline-status-badge.completed {
            background-color: rgba(0, 230, 118, 0.06);
            color: var(--color-success);
            border-color: rgba(0, 230, 118, 0.2);
            box-shadow: 0 0 15px rgba(0, 230, 118, 0.08);
        }

        .header-right {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .session-timer {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 18px;
            border-radius: 30px;
            border: 1px solid rgba(0, 242, 254, 0.15);
            background-color: rgba(0, 242, 254, 0.04);
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            font-weight: 700;
            color: var(--accent-teal);
            transition: all 0.3s ease;
            letter-spacing: 0.5px;
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.04);
        }

        .session-timer.warning {
            border-color: rgba(255, 214, 0, 0.3);
            background-color: rgba(255, 214, 0, 0.04);
            color: var(--color-warning);
            box-shadow: 0 0 15px rgba(255, 214, 0, 0.06);
        }

        .session-timer.critical {
            border-color: rgba(255, 23, 68, 0.3);
            background-color: rgba(255, 23, 68, 0.04);
            color: var(--color-danger);
            box-shadow: 0 0 18px rgba(255, 23, 68, 0.1);
            animation: pulse 1.2s infinite;
        }

        .session-timer.expired {
            border-color: rgba(255, 23, 68, 0.5);
            background-color: rgba(255, 23, 68, 0.08);
            color: var(--color-danger);
        }

        .dashboard-container {
            display: grid;
            grid-template-columns: 1.80fr 1.20fr;
            gap: 30px;
            padding: 30px 40px;
            max-width: 1680px;
            margin: 0 auto;
            width: 100%;
            flex-grow: 1;
        }

        .panel {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 30px;
            backdrop-filter: blur(25px);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
            display: flex;
            flex-direction: column;
            gap: 25px;
            transition: border-color 0.3s ease;
        }

        .panel:hover {
            border-color: rgba(255, 255, 255, 0.08);
        }

        .panel-title {
            font-size: 20px;
            font-weight: 700;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 15px;
            color: var(--text-primary);
            letter-spacing: 0.25px;
        }

        /* ------------------ STATS CARDS ------------------ */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.01);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px 12px;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 120px;
            height: 120px;
            background: radial-gradient(circle, rgba(0, 242, 254, 0.05) 0%, transparent 70%);
            transform: translate(-50%, -50%);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .stat-card:hover::before {
            opacity: 1;
        }

        .stat-card:hover {
            border-color: rgba(0, 242, 254, 0.2);
            background: rgba(255, 255, 255, 0.02);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        }

        .stat-value {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 4px;
            background: linear-gradient(135deg, #ffffff, var(--text-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stat-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
            font-weight: 600;
        }

        /* ------------------ ALPHA CARD QUEUE ------------------ */
        .alpha-list {
            display: flex;
            flex-direction: column;
            gap: 16px;
            max-height: 520px;
            overflow-y: auto;
            padding-right: 6px;
        }

        .alpha-card {
            background: rgba(255, 255, 255, 0.015);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            padding: 20px;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .alpha-card:hover {
            transform: translateY(-2px);
            border-color: rgba(0, 242, 254, 0.2);
            background: rgba(255, 255, 255, 0.03);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        }

        .alpha-card.simulating {
            border-color: rgba(0, 176, 255, 0.35);
            background: rgba(0, 176, 255, 0.02);
            box-shadow: 0 0 20px rgba(0, 176, 255, 0.06);
        }

        .alpha-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .alpha-id-tag {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: var(--accent-teal);
            font-weight: 700;
        }

        .alpha-formula {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            background-color: rgba(0, 0, 0, 0.35);
            padding: 10px 14px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.01);
            word-break: break-all;
            color: #cbd5e1;
            line-height: 1.45;
        }

        .alpha-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: var(--text-secondary);
        }

        .alpha-metrics {
            display: flex;
            gap: 12px;
        }

        .metric-badge {
            background: rgba(255, 255, 255, 0.02);
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 11px;
            border: 1px solid rgba(255, 255, 255, 0.04);
            font-family: 'JetBrains Mono', monospace;
        }

        .metric-badge span {
            font-weight: 700;
            color: var(--text-primary);
        }

        .status-badge {
            font-size: 10px;
            font-weight: 800;
            padding: 5px 12px;
            border-radius: 20px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .status-badge.pending { background-color: rgba(255, 255, 255, 0.04); color: var(--text-secondary); border: 1px solid rgba(255, 255, 255, 0.04); }
        .status-badge.simulating { background-color: rgba(0, 176, 255, 0.1); color: var(--color-info); border: 1px solid rgba(0, 176, 255, 0.25); animation: pulse 1.5s infinite; }
        .status-badge.evaluating { background-color: rgba(255, 214, 0, 0.1); color: var(--color-warning); border: 1px solid rgba(255, 214, 0, 0.25); }
        .status-badge.submitted { background-color: rgba(0, 230, 118, 0.1); color: var(--color-success); border: 1px solid rgba(0, 230, 118, 0.25); }
        .status-badge.soft_fail { background-color: rgba(255, 214, 0, 0.1); color: var(--color-warning); border: 1px solid rgba(255, 214, 0, 0.2); }
        .status-badge.hard_reject { background-color: rgba(255, 23, 68, 0.1); color: var(--color-danger); border: 1px solid rgba(255, 23, 68, 0.2); }
        .status-badge.error { background-color: rgba(255, 23, 68, 0.1); color: var(--color-danger); border: 1px solid rgba(255, 23, 68, 0.2); }

        .progress-bar-container {
            width: 100%;
            height: 5px;
            background-color: rgba(255, 255, 255, 0.03);
            border-radius: 4px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-teal), var(--accent-blue));
            width: 0%;
            transition: width 0.5s ease;
        }

        /* ------------------ SIDE PANEL (WORDS / RULES) ------------------ */
        .side-panels-container {
            display: flex;
            flex-direction: column;
            gap: 30px;
        }

        /* 3 Magic Words Section */
        .manifest-title {
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--accent-teal);
            margin-bottom: 12px;
        }

        .manifest-grid {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .manifest-card {
            background: rgba(255, 255, 255, 0.015);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            position: relative;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .manifest-card:hover {
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.025);
            border-color: rgba(0, 242, 254, 0.2);
            box-shadow: 0 6px 20px rgba(0, 242, 254, 0.05);
        }

        .manifest-card::before {
            content: 'MAGIC WORD';
            position: absolute;
            top: 14px;
            right: 16px;
            font-size: 8px;
            font-weight: 800;
            letter-spacing: 0.5px;
            padding: 2px 6px;
            border-radius: 4px;
        }

        .manifest-card.login::before { background: rgba(255, 214, 0, 0.1); color: var(--color-warning); }
        .manifest-card.start::before { background: rgba(0, 242, 254, 0.1); color: var(--accent-teal); }
        .manifest-card.push::before { background: rgba(0, 230, 118, 0.1); color: var(--color-success); }
        .manifest-card.load::before { background: rgba(0, 176, 255, 0.1); color: var(--color-info); }

        .manifest-word {
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            font-weight: 700;
            color: var(--text-primary);
        }

        .manifest-desc {
            font-size: 11px;
            color: var(--text-secondary);
            line-height: 1.4;
        }

        /* Logs Panel */
        .logs-panel {
            display: flex;
            flex-direction: column;
            flex-grow: 1;
            height: 100%;
        }

        .logs-container {
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            background-color: rgba(0, 0, 0, 0.45);
            border-radius: 16px;
            padding: 18px;
            flex-grow: 1;
            overflow-y: auto;
            border: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            gap: 8px;
            color: #94a3b8;
            max-height: 290px;
            box-shadow: inset 0 4px 20px rgba(0, 0, 0, 0.4);
        }

        .log-entry {
            line-height: 1.5;
            word-break: break-all;
        }

        .log-entry.info { color: #94a3b8; }
        .log-entry.warning { color: var(--color-warning); }
        .log-entry.error { color: var(--color-danger); }
        .log-entry.success { color: var(--color-success); }

        @keyframes pulse {
            0% { opacity: 0.5; }
            50% { opacity: 1; }
            100% { opacity: 0.5; }
        }

        /* Scrollbars */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--accent-teal);
        }
    </style>
</head>
<body>
    <header>
        <div class="logo">AlphaForge Pipeline</div>
        <div class="header-right">
            <div id="session-timer" class="session-timer" title="WorldQuant Brain session time remaining">
                <span class="timer-icon">&#128274;</span>
                <span id="session-countdown">Loading...</span>
            </div>
            <div id="pipeline-status" class="pipeline-status-badge running">
                Pipeline Active
            </div>
        </div>
    </header>

    <div class="dashboard-container">
        <!-- Left Panel: Simulation Queue and Progress -->
        <div class="panel">
            <div class="panel-title">
                <span>Simulation Queue Execution</span>
                <span id="queue-count" style="font-size: 14px; color: var(--text-secondary)">0 / 5 Completed</span>
            </div>

            <!-- Dynamic Research & Alpha Synthesis Panel -->
            <div class="research-synthesis-panel" style="background: rgba(0, 242, 254, 0.02); border: 1px solid rgba(0, 242, 254, 0.1); border-radius: 18px; padding: 20px; display: flex; flex-direction: column; gap: 12px; margin-bottom: 5px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 14px; font-weight: 700; color: var(--accent-teal); display: flex; align-items: center; gap: 8px; letter-spacing: 0.5px;">
                        <span>🔬</span> DYNAMIC RESEARCH MANUAL & GENERATION BLUEPRINT
                    </div>
                    <a href="file:///c:/Users/Admin/Documents/VIBE_YT/wq/research.md" target="_blank" style="font-size: 11px; color: var(--accent-blue); text-decoration: none; font-weight: 600; border: 1px solid rgba(79, 172, 254, 0.2); padding: 4px 12px; border-radius: 8px; background: rgba(79, 172, 254, 0.05); transition: all 0.3s ease;">
                        OPEN RESEARCH.MD ↗
                    </a>
                </div>
                <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.5;">
                    To generate a qualifying alpha that satisfies platform guidelines, always synthesize your factor using the <strong>Gated Reversion Blueprint</strong>. This pattern smooths raw signals to limit turnover and gates trading on liquid days.
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1.2fr; gap: 14px; align-items: center;">
                    <div style="background: rgba(0, 0, 0, 0.25); border: 1px solid rgba(255, 255, 255, 0.02); border-radius: 10px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                        <div style="font-size: 10.5px; font-weight: 700; color: var(--text-primary); letter-spacing: 0.5px;">🎛️ SWEET-SPOT PARAMETERS</div>
                        <div style="font-size: 9.5px; color: var(--text-secondary); display: flex; flex-direction: column; gap: 5px;">
                            <div>• <strong>Smoothing Decay</strong>: <code>3</code> to <code>5</code> days</div>
                            <div>• <strong>Liquidity Gate</strong>: <code>adv20 * 0.6</code></div>
                            <div>• <strong>Peer Group</strong>: <code>SUBINDUSTRY</code></div>
                        </div>
                    </div>
                    <div style="background: rgba(0, 0, 0, 0.25); border: 1px solid rgba(255, 255, 255, 0.02); border-radius: 10px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                        <div style="font-size: 10.5px; font-weight: 700; color: var(--accent-teal); letter-spacing: 0.5px;">🧪 MATHEMATICAL TEMPLATE</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #cbd5e1; line-height: 1.4; word-break: break-all;">
                            group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(SIGNAL, 3)), 0), subindustry)
                        </div>
                    </div>
                </div>
            </div>

            <!-- Stats Grid -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div id="stat-total" class="stat-value">5</div>
                    <div class="stat-label">Total Alphas</div>
                </div>
                <div class="stat-card">
                    <div id="stat-simulating" class="stat-value">0</div>
                    <div class="stat-label">Active Running</div>
                </div>
                <div class="stat-card">
                    <div id="stat-passed" class="stat-value" style="color: var(--color-success)">0</div>
                    <div class="stat-label">Submitted</div>
                </div>
                <div class="stat-card">
                    <div id="stat-failed" class="stat-value" style="color: var(--color-danger)">0</div>
                    <div class="stat-label">Failed/Error</div>
                </div>
            </div>

            <!-- Active List of Queue -->
            <div id="alpha-list" class="alpha-list">
                <!-- Dynamically populated -->
            </div>
        </div>

        <!-- Right Panel: Commands, Rules & Logs -->
        <div class="side-panels-container">
            <!-- 3 Magic Code Words -->
            <div class="panel">
                <div class="manifest-title">⚡ Session Magic Code Words</div>
                <div class="manifest-grid">
                    <div class="manifest-card login">
                        <div class="manifest-word">LOGIN</div>
                        <div class="manifest-desc">Authenticates WQ session, updates cookies cache, and verifies connectivity status.</div>
                    </div>
                    <div class="manifest-card start">
                        <div class="manifest-word">START PIPELINE</div>
                        <div class="manifest-desc">Initiates ThreadPoolExecutor executing exactly 3 concurrent simulations, spacing POSTs by 20s.</div>
                    </div>
                    <div class="manifest-card push">
                        <div class="manifest-word">PUSH CODES</div>
                        <div class="manifest-desc">Appends new unique pricing/volume alphas to the active simulation queue (python manage_queue.py append).</div>
                    </div>
                    <div class="manifest-card load">
                        <div class="manifest-word">LOAD CODES</div>
                        <div class="manifest-desc">Replaces the active queue completely with a fresh batch of 5 pricing/volume alphas (python manage_queue.py replace).</div>
                    </div>
                </div>
            </div>



            <!-- Logs Panel -->
            <div class="panel logs-panel">
                <div class="panel-title">Pipeline Output Logs</div>
                <div id="logs-container" class="logs-container">
                    <!-- Dynamically populated -->
                </div>
            </div>
        </div>
    </div>

    <script>
        const statusMap = {
            'PENDING': 'pending',
            'SIMULATING': 'simulating',
            'EVALUATING': 'evaluating',
            'SUBMITTED': 'submitted',
            'SOFT_FAIL': 'soft_fail',
            'HARD_REJECT': 'hard_reject',
            'ERROR': 'error'
        };

        let lastLogCount = 0;

        async function updateDashboard() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();

                // Update pipeline status badge
                const statusBadge = document.getElementById('pipeline-status');
                if (data.status === 'RUNNING') {
                    statusBadge.className = 'pipeline-status-badge running';
                    statusBadge.innerHTML = 'Pipeline Active';
                } else {
                    statusBadge.className = 'pipeline-status-badge completed';
                    statusBadge.innerHTML = 'Pipeline Finished';
                }

                // Update stats
                let activeCount = 0;
                let passedCount = 0;
                let failedCount = 0;
                let completedCount = 0;

                data.alphas.forEach(alpha => {
                    if (alpha.status === 'SIMULATING' || alpha.status === 'EVALUATING') {
                        activeCount++;
                    } else if (alpha.status === 'SUBMITTED') {
                        passedCount++;
                        completedCount++;
                    } else if (['HARD_REJECT', 'SOFT_FAIL', 'ERROR'].includes(alpha.status)) {
                        failedCount++;
                        completedCount++;
                    }
                });

                document.getElementById('stat-simulating').innerText = activeCount;
                document.getElementById('stat-passed').innerText = passedCount;
                document.getElementById('stat-failed').innerText = failedCount;
                document.getElementById('stat-total').innerText = data.alphas.length;
                document.getElementById('queue-count').innerText = `${completedCount} / ${data.alphas.length} Completed`;



                // Update alpha list
                const listContainer = document.getElementById('alpha-list');
                listContainer.innerHTML = '';

                data.alphas.forEach((alpha, index) => {
                    const card = document.createElement('div');
                    card.className = `alpha-card ${alpha.status === 'SIMULATING' ? 'simulating' : ''}`;

                    const sharpeVal = alpha.sharpe !== null ? alpha.sharpe.toFixed(2) : '-';
                    const fitnessVal = alpha.fitness !== null ? alpha.fitness.toFixed(2) : '-';
                    const turnoverVal = alpha.turnover !== null ? alpha.turnover.toFixed(1) + '%' : '-';

                    card.innerHTML = `
                        <div class="alpha-header">
                            <span class="alpha-id-tag">[Alpha #${index + 1}] ${alpha.family}</span>
                            <span class="status-badge ${statusMap[alpha.status]}">${alpha.status}</span>
                        </div>
                        <div class="alpha-formula">${alpha.formula}</div>
                        <div class="alpha-meta">
                            <div class="alpha-metrics">
                                <div class="metric-badge">Sharpe: <span>${sharpeVal}</span></div>
                                <div class="metric-badge">Fitness: <span>${fitnessVal}</span></div>
                                <div class="metric-badge">Turnover: <span>${turnoverVal}</span></div>
                            </div>
                            <div style="font-size: 11px; max-width: 50%; text-align: right; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">
                                ${alpha.error_message ? `<span style="color: var(--color-danger)" title="${alpha.error_message}">${alpha.error_message}</span>` : alpha.hypothesis}
                            </div>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar" style="width: ${alpha.progress}%"></div>
                        </div>
                    `;
                    listContainer.appendChild(card);
                });

                // Update logs
                const logsContainer = document.getElementById('logs-container');
                if (data.logs.length > lastLogCount) {
                    for (let i = lastLogCount; i < data.logs.length; i++) {
                        const entry = document.createElement('div');
                        entry.className = 'log-entry';
                        
                        const text = data.logs[i];
                        if (text.includes('[ERROR]') || text.includes('failed')) {
                            entry.className += ' error';
                        } else if (text.includes('[SUBMITTED]') || text.includes('SUBMITTABLE')) {
                            entry.className += ' success';
                        } else if (text.includes('[WARNING]') || text.includes('cooldown') || text.includes('Rate limit')) {
                            entry.className += ' warning';
                        } else {
                            entry.className += ' info';
                        }
                        
                        entry.innerText = text;
                        logsContainer.appendChild(entry);
                    }
                    logsContainer.scrollTop = logsContainer.scrollHeight;
                    lastLogCount = data.logs.length;
                }

            } catch (e) {
                console.error("Dashboard error:", e);
            }
        }

        // Poll dashboard every 2 seconds
        setInterval(updateDashboard, 2000);
        updateDashboard();

        // Session countdown timer
        let sessionExpiry = null;

        async function updateSessionTimer() {
            try {
                if (!sessionExpiry) {
                    const res = await fetch('/api/session');
                    const data = await res.json();
                    sessionExpiry = data.exp_epoch;
                }

                const now = Math.floor(Date.now() / 1000);
                const remaining = sessionExpiry - now;
                const el = document.getElementById('session-countdown');
                const widget = document.getElementById('session-timer');

                if (remaining <= 0) {
                    el.textContent = 'SESSION EXPIRED';
                    widget.className = 'session-timer expired';
                    return;
                }

                const h = Math.floor(remaining / 3600);
                const m = Math.floor((remaining % 3600) / 60);
                const s = remaining % 60;
                const label = (h > 0 ? h + 'h ' : '') + m + 'm ' + String(s).padStart(2, '0') + 's';
                el.textContent = label;

                if (remaining < 600) {  // < 10 min
                    widget.className = 'session-timer critical';
                } else if (remaining < 1800) {  // < 30 min
                    widget.className = 'session-timer warning';
                } else {
                    widget.className = 'session-timer';
                }
            } catch(e) {
                document.getElementById('session-countdown').textContent = 'N/A';
            }
        }

        setInterval(updateSessionTimer, 1000);
        updateSessionTimer();
    </script>
</body>
</html>
"""

@app.route("/")
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route("/api/status")
def get_status():
    """Dynamically reconstruct pipeline_state from SQLite database and queue file
    to support multi-process WSGI/Gunicorn environments perfectly.
    """
    import sqlite3
    
    # 1. Initialize DB if not done already (ensures tables exist)
    try:
        init_db()
    except Exception:
        pass

    # 2. Read simulation queue from disk
    queue_path = Path("db") / "simulation_queue.json"
    tasks = []
    if queue_path.exists():
        try:
            with open(queue_path, "r") as f:
                tasks = json.load(f)
        except Exception:
            tasks = []

    # 3. Read latest runs from SQLite database
    runs = {}
    db_path = Path("db") / "alpha_vault.db"
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT formula, sharpe, fitness, turnover, status, error_message FROM alpha_runs")
            for row in cursor.fetchall():
                # Map formula to its simulation results
                runs[row[0]] = {
                    "sharpe": row[1],
                    "fitness": row[2],
                    "turnover": row[3],
                    "status": row[4],
                    "error_message": row[5]
                }
            conn.close()
        except Exception:
            pass

    # 4. Construct live state dynamically
    alphas_state = []
    for idx, task in enumerate(tasks):
        formula = task["formula"]
        run_info = runs.get(formula, {})
        status = run_info.get("status", "PENDING")
        
        alphas_state.append({
            "formula": formula,
            "family": task.get("family", "Unknown"),
            "hypothesis": task.get("hypothesis", ""),
            "status": status,
            "progress": 100 if status in ("SUBMITTED", "HARD_REJECT", "SOFT_FAIL", "ERROR") else 0,
            "sharpe": run_info.get("sharpe"),
            "fitness": run_info.get("fitness"),
            "turnover": run_info.get("turnover"),
            "error_message": run_info.get("error_message")
        })

    # Read the dynamic status
    is_completed = len(alphas_state) > 0 and all(a["status"] in ("SUBMITTED", "HARD_REJECT", "SOFT_FAIL", "ERROR") for a in alphas_state)
    status_str = "COMPLETED" if is_completed else "RUNNING"

    # Merge any in-memory logs (process-local)
    logs = pipeline_state.get("logs", [])
    
    # Also fetch database entries to show run activity in logs if empty
    if not logs and db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, formula, status, sharpe FROM alpha_runs ORDER BY id DESC LIMIT 30")
            for row in cursor.fetchall():
                sharpe_val = f"Sharpe: {row[3]:.2f}" if row[3] is not None else "No Sharpe"
                logs.append(f"[{row[0]}] [DATABASE] {row[2]} | {row[1][:60]}... | {sharpe_val}")
            conn.close()
            logs.reverse() # chronologically oldest to newest for UI log panel
        except Exception:
            pass

    return jsonify({
        "status": status_str,
        "alphas": alphas_state,
        "logs": logs
    })

@app.route("/api/session")
def get_session():
    """Decode the session JWT and return expiry info."""
    try:
        cookie_files = list(Path("db").glob("session_cookies_*.json"))
        if not cookie_files:
            return jsonify({"error": "No session file found", "exp_epoch": 0})
        with open(cookie_files[0]) as f:
            cookies = json.load(f)
        token = cookies.get("t", "")
        if not token:
            return jsonify({"error": "No token in cookie file", "exp_epoch": 0})
        payload_b64 = token.split(".")[1]
        padding = 4 - len(payload_b64) % 4
        payload_b64 += "=" * padding
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        exp = payload.get("exp", 0)
        now = int(time.time())
        remaining = max(0, exp - now)
        return jsonify({
            "exp_epoch": exp,
            "remaining_seconds": remaining,
            "expired": remaining == 0
        })
    except Exception as e:
        return jsonify({"error": str(e), "exp_epoch": 0})

@app.route("/api/queue-alpha", methods=["POST"])
def queue_alpha():
    """Secure endpoint: inject new alphas into the live queue from this chat.
    Requires Bearer token matching API_SECRET_TOKEN env var.
    Body: [{"formula": "...", "family": "...", "hypothesis": "...", "settings": {...}}]
    """
    # --- Auth check ---
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    if token != API_SECRET_TOKEN:
        return jsonify({"error": "Unauthorized", "hint": "Provide valid Bearer token"}), 401

    # --- Parse body ---
    try:
        data = request.get_json(force=True)
        if not isinstance(data, list):
            data = [data]  # Accept single object or array
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    # --- Validate and append each alpha ---
    added = []
    skipped = []
    queue_path = Path("db") / "simulation_queue.json"

    # Load current queue from disk
    existing_queue = []
    if queue_path.exists():
        try:
            with open(queue_path) as f:
                existing_queue = json.load(f)
        except Exception:
            existing_queue = []

    existing_formulas = {a.get("formula", "") for a in existing_queue}
    # Also skip formulas already in memory
    existing_formulas.update(a["formula"] for a in pipeline_state["alphas"])

    for item in data:
        formula = item.get("formula", "").strip()
        if not formula:
            skipped.append({"reason": "Missing formula", "item": item})
            continue
        if formula in existing_formulas:
            skipped.append({"reason": "Already queued", "formula": formula})
            continue

        task = {
            "family": item.get("family", "API Injected"),
            "hypothesis": item.get("hypothesis", "Injected via secure API bridge"),
            "formula": formula,
            "settings": item.get("settings", {
                "decay": 5, "neutralization": "SUBINDUSTRY",
                "universe": "TOP3000", "truncation": 0.08
            })
        }

        # Append to disk queue
        existing_queue.append(task)
        existing_formulas.add(formula)
        added.append(formula)
        log_message("INFO", f"[API] Queued new alpha via API bridge: {formula[:80]}...")

    # Save updated queue to disk
    queue_path.parent.mkdir(exist_ok=True)
    with open(queue_path, "w") as f:
        json.dump(existing_queue, f, indent=2)

    return jsonify({
        "status": "ok",
        "added": len(added),
        "skipped": len(skipped),
        "added_formulas": added,
        "skipped_details": skipped
    })

@app.route("/api/queue-status", methods=["GET"])
def queue_status():
    """Returns a lightweight summary of the live queue — no auth needed for read."""
    queue_path = Path("db") / "simulation_queue.json"
    try:
        with open(queue_path) as f:
            q = json.load(f)
    except Exception:
        q = []
    return jsonify({
        "queue_on_disk": len(q),
        "in_memory": len(pipeline_state["alphas"]),
        "pipeline_status": pipeline_state["status"],
        "formulas": [a.get("formula", "")[:80] for a in q]
    })

def run_flask():
    # Run Flask server — binds to 0.0.0.0 on Render, falls back to 8000 locally
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0" if os.environ.get("RENDER") else "127.0.0.1"
    app.run(host=host, port=port, debug=False, use_reloader=False)

def robust_request(session, method, url, index=None, **kwargs):
    """Sends an API request and automatically retries forever if a local network/DNS failure occurs."""
    import requests
    while True:
        try:
            if 'timeout' not in kwargs:
                kwargs['timeout'] = 30
            return session.request(method, url, **kwargs)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ChunkedEncodingError) as e:
            lbl = f"Alpha #{index+1}: " if index is not None else ""
            log_message("WARNING", f"{lbl}Network connection dropped. Patiently retrying in 30 seconds... (Reason: {e})")
            time.sleep(30)

def simulate_task(index, task, session):
    run_uuid = str(uuid.uuid4())[:8]
    family = task["family"]
    hypothesis = task["hypothesis"]
    formula = task["formula"]
    settings = dict(DEFAULT_SIM_SETTINGS)
    if "settings" in task and task["settings"]:
        settings.update(task["settings"])

    # Check database cache to see if already simulated
    cached = check_already_simulated(formula)
    if cached:
        log_message("INFO", f"Alpha #{index+1}: Found cached simulation result in database. Skipping repeat API submission.")
        pipeline_state["alphas"][index]["status"] = cached["status"]
        pipeline_state["alphas"][index]["progress"] = 100
        pipeline_state["alphas"][index]["sharpe"] = cached["sharpe"]
        pipeline_state["alphas"][index]["fitness"] = cached["fitness"]
        pipeline_state["alphas"][index]["turnover"] = cached["turnover"]
        pipeline_state["alphas"][index]["error_message"] = cached["error_message"]
        return

    pipeline_state["alphas"][index]["status"] = "SIMULATING"
    pipeline_state["alphas"][index]["progress"] = 10
    log_message("INFO", f"Alpha #{index+1}: Initiating simulation for {formula}")

    # Local Syntax and Operator validation
    from src.validator import validate_fastexpr
    is_valid, err = validate_fastexpr(formula)
    if not is_valid:
        err_msg = f"Local Validation Failed: {err}"
        log_message("ERROR", f"Alpha #{index+1}: {err_msg}")
        pipeline_state["alphas"][index]["status"] = "ERROR"
        pipeline_state["alphas"][index]["error_message"] = err_msg
        save_alpha_run({
            "run_id": run_uuid, "family": family, "hypothesis": hypothesis, "formula": formula,
            "region": settings.get("region", "USA"),
            "universe": settings.get("universe", "TOP3000"),
            "neutralization": settings.get("neutralization", "SUBINDUSTRY"),
            "decay": settings.get("decay", 6),
            "truncation": settings.get("truncation", 0.08),
            "delay": settings.get("delay", 1),
            "sharpe": None, "fitness": None, "turnover": None,
            "checks_passed": 0, "weight_check": "FAIL", "sub_sharpe": None, "status": "ERROR",
            "alpha_link": None, "sim_link": None, "error_message": err_msg,
            "llm_model": "gemini-1.5-flash", "parent_id": None
        })
        return

    # Build WQ simulation submission body
    payload = {
        "regular": formula,
        "type": "REGULAR",
        "settings": {
            "nanHandling": settings.get("nanHandling", "OFF"),
            "instrumentType": settings.get("instrumentType", "EQUITY"),
            "delay": settings.get("delay", 1),
            "universe": settings.get("universe", "TOP3000"),
            "truncation": settings.get("truncation", 0.08),
            "unitHandling": settings.get("unitHandling", "VERIFY"),
            "pasteurization": settings.get("pasteurization", "ON"),
            "region": settings.get("region", "USA"),
            "language": "FASTEXPR",
            "decay": settings.get("decay", 6),
            "neutralization": settings.get("neutralization", "SUBINDUSTRY"),
            "visualization": False
        }
    }

    # API request
    try:
        # Acquire submission lock to ensure sequential spaced requests
        with submission_lock:
            # Enforce 20-second spacing between concurrent thread submissions
            log_message("INFO", f"Alpha #{index+1}: Enforcing 20s submission rate-limit spacing...")
            time.sleep(20)
            r = robust_request(session, "POST", WQ_SIM_URL, index=index, json=payload, timeout=30)
            
        if r.status_code == 429:
            import random
            retry_wait = 30 + random.uniform(5, 15)
            log_message("WARNING", f"Alpha #{index+1}: Rate limit exceeded (HTTP 429). Jittered retry in {retry_wait:.1f} seconds...")
            pipeline_state["alphas"][index]["status"] = "PENDING"
            pipeline_state["alphas"][index]["progress"] = 0
            time.sleep(retry_wait)
            return simulate_task(index, task, session)  # Recursive retry
            
        if r.status_code not in [200, 201]:
            err_msg = f"HTTP {r.status_code}: {r.text}"
            log_message("ERROR", f"Alpha #{index+1} Submission failed: {err_msg}")
            pipeline_state["alphas"][index]["status"] = "ERROR"
            pipeline_state["alphas"][index]["error_message"] = err_msg
            save_alpha_run({
                "run_id": run_uuid, "family": family, "hypothesis": hypothesis, "formula": formula,
                "region": settings.get("region", "USA"),
                "universe": settings.get("universe", "TOP3000"),
                "neutralization": settings.get("neutralization", "SUBINDUSTRY"),
                "decay": settings.get("decay", 6),
                "truncation": settings.get("truncation", 0.08),
                "delay": settings.get("delay", 1),
                "sharpe": None, "fitness": None, "turnover": None,
                "checks_passed": 0, "weight_check": "FAIL", "sub_sharpe": None, "status": "ERROR",
                "alpha_link": None, "sim_link": None, "error_message": err_msg,
                "llm_model": "gemini-1.5-flash", "parent_id": None
            })
            return

        if 'Location' not in r.headers:
            err_msg = "Location header missing in API response."
            log_message("ERROR", f"Alpha #{index+1}: {err_msg}")
            pipeline_state["alphas"][index]["status"] = "ERROR"
            pipeline_state["alphas"][index]["error_message"] = err_msg
            return

        nxt_url = r.headers['Location']
        pipeline_state["alphas"][index]["progress"] = 35
        log_message("INFO", f"Alpha #{index+1}: Simulation queued successfully. Link: {nxt_url}")

    except Exception as e:
        log_message("ERROR", f"Alpha #{index+1} Exception: {e}")
        pipeline_state["alphas"][index]["status"] = "ERROR"
        pipeline_state["alphas"][index]["error_message"] = str(e)
        return

    # Polling Loop
    retry_count = 0
    alpha_id = None
    while True:
        try:
            poll_r = robust_request(session, "GET", nxt_url, index=index, timeout=30)
            if poll_r.status_code == 429:
                time.sleep(15 + random.uniform(2, 6))
                continue
            if poll_r.status_code != 200:
                log_message("WARNING", f"Alpha #{index+1} poll HTTP status: {poll_r.status_code}")
                time.sleep(10 + random.uniform(1, 4))
                continue

            res = poll_r.json()
            if 'alpha' in res:
                alpha_id = res['alpha']
                log_message("INFO", f"Alpha #{index+1}: Simulation calculations completed on WQ cluster.")
                break

            progress = int(res.get('progress', 0) * 100)
            pipeline_state["alphas"][index]["progress"] = max(35, progress)
            log_message("INFO", f"Alpha #{index+1}: WorldQuant backtesting progress... {progress}%")

            if 'message' in res and 'error' in str(res.get('message', '')).lower():
                err_msg = res['message']
                log_message("ERROR", f"Alpha #{index+1} Syntax Check Failed: {err_msg}")
                pipeline_state["alphas"][index]["status"] = "ERROR"
                pipeline_state["alphas"][index]["error_message"] = err_msg
                save_alpha_run({
                    "run_id": run_uuid, "family": family, "hypothesis": hypothesis, "formula": formula,
                    "region": settings.get("region", "USA"),
                    "universe": settings.get("universe", "TOP3000"),
                    "neutralization": settings.get("neutralization", "SUBINDUSTRY"),
                    "decay": settings.get("decay", 6),
                    "truncation": settings.get("truncation", 0.08),
                    "delay": settings.get("delay", 1),
                    "sharpe": None, "fitness": None, "turnover": None,
                    "checks_passed": 0, "weight_check": "FAIL", "sub_sharpe": None, "status": "HARD_REJECT",
                    "alpha_link": None, "sim_link": nxt_url, "error_message": err_msg,
                    "llm_model": "gemini-1.5-flash", "parent_id": None
                })
                return
        except Exception as e:
            log_message("ERROR", f"Alpha #{index+1} Polling error: {e}")
            retry_count += 1
            if retry_count > 10:
                pipeline_state["alphas"][index]["status"] = "ERROR"
                pipeline_state["alphas"][index]["error_message"] = f"Polling errors exceeded limit: {e}"
                return
        time.sleep(15)

    # Simulation Complete - Retrieve metrics
    pipeline_state["alphas"][index]["status"] = "EVALUATING"
    pipeline_state["alphas"][index]["progress"] = 90
    try:
        alpha_url = f"{WQ_ALPHAS_URL}/{alpha_id}"
        alpha_r = robust_request(session, "GET", alpha_url, index=index, timeout=30).json()

        # Extract metrics
        metrics = alpha_r.get("is", {})
        sharpe = metrics.get("sharpe")
        fitness = metrics.get("fitness")
        turnover = metrics.get("turnover", 0.0) * 100.0  # Convert to percent

        # Extract checks
        checks_passed = 0
        weight_check = "FAIL"
        sub_sharpe = -1.0

        checks = metrics.get("checks", [])
        for check in checks:
            if check.get("result") == "PASS":
                checks_passed += 1
            if check.get("name") == "CONCENTRATED_WEIGHT":
                weight_check = check.get("result", "FAIL")
            if check.get("name") == "SUB-UNIVERSE_SHARPE":
                # Find sub sharpe value if present
                sub_sharpe = 1.0 if check.get("result") == "PASS" else -1.0

        sim_res = {
            "status": "OK",
            "sharpe": sharpe,
            "fitness": fitness,
            "turnover": turnover,
            "checks_passed": checks_passed,
            "weight_check": weight_check,
            "sub_sharpe": sub_sharpe,
            "alpha_link": f"https://brain.worldquant.com/alpha/{alpha_id}",
            "sim_link": nxt_url,
            "alpha_id": alpha_id,
            "error_message": None
        }

        status = evaluate_alpha_metrics(sim_res)
        pipeline_state["alphas"][index]["status"] = status
        pipeline_state["alphas"][index]["progress"] = 100
        pipeline_state["alphas"][index]["sharpe"] = sharpe
        pipeline_state["alphas"][index]["fitness"] = fitness
        pipeline_state["alphas"][index]["turnover"] = turnover

        run_data = {
            "run_id": run_uuid, "family": family, "hypothesis": hypothesis, "formula": formula,
            "region": settings.get("region", "USA"),
            "universe": settings.get("universe", "TOP3000"),
            "neutralization": settings.get("neutralization", "SUBINDUSTRY"),
            "decay": settings.get("decay", 6),
            "truncation": settings.get("truncation", 0.08),
            "delay": settings.get("delay", 1),
            "sharpe": sharpe, "fitness": fitness, "turnover": turnover,
            "checks_passed": checks_passed, "weight_check": weight_check, "sub_sharpe": sub_sharpe,
            "status": status, "alpha_link": sim_res["alpha_link"], "sim_link": nxt_url,
            "error_message": None, "llm_model": "gemini-1.5-flash", "parent_id": None
        }

        row_id = save_alpha_run(run_data)

        # Save successful alphas to files
        if status in ("SUBMITTED", "SOFT_FAIL") and alpha_id:
            try:
                out_dir = Path(ALPHAS_OUT_DIR)
                out_dir.mkdir(parents=True, exist_ok=True)
                alpha_file = out_dir / f"alpha_{alpha_id}.json"
                with open(alpha_file, "w") as f:
                    json.dump({
                        "alpha_id": alpha_id,
                        "formula": formula,
                        "family": family,
                        "hypothesis": hypothesis,
                        "status": status,
                        "sharpe": sharpe,
                        "fitness": fitness,
                        "turnover": turnover,
                        "settings": settings,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }, f, indent=2)
                log_message("SUBMITTED", f"Alpha #{index+1} SAVED to file: {alpha_file.name}")
            except Exception as e:
                log_message("ERROR", f"Failed to save alpha file: {e}")

        # Auto-submit and poll checks if it qualifies
        if status == "SUBMITTED":
            log_message("SUBMITTED", f"Alpha #{index+1} qualifies! Starting submission checks for ID: {alpha_id}")
            sub_url = f"{WQ_ALPHAS_URL}/{alpha_id}/submit"
            submit_r = robust_request(session, "POST", sub_url, index=index, timeout=30)
            
            if submit_r.status_code in (200, 201):
                log_message("SUBMITTED", f"Alpha #{index+1}: Submission checks initiated. Polling for completion...")
                
                # Step 2: Poll GET /submit until 404 (success) per API spec
                poll_limit = 40
                submitted_ok = False
                for poll_i in range(poll_limit):
                    time.sleep(15 + random.uniform(1, 4))
                    poll_sub = robust_request(session, "GET", sub_url, index=index, timeout=30)
                    if poll_sub.status_code == 404:
                        # 404 = checks done, alpha is on production board
                        log_message("SUBMITTED", f"Alpha #{index+1} FULLY SUBMITTED to production board! ID: {alpha_id}")
                        save_submitted_alpha(row_id, alpha_id, self_corr_pass=True)
                        submitted_ok = True
                        break
                    elif poll_sub.status_code == 403:
                        # 403 = submission failed (e.g. PROD_CORRELATION failure)
                        err_detail = ""
                        try:
                            checks_data = poll_sub.json().get("is", {}).get("checks", [])
                            failed = [c for c in checks_data if c.get("result") == "FAIL"]
                            err_detail = "; ".join([f"{c['name']}={c.get('value','')}" for c in failed])
                        except Exception:
                            err_detail = poll_sub.text[:200]
                        log_message("WARNING", f"Alpha #{index+1} submission REJECTED by WQ checks: {err_detail}")
                        pipeline_state["alphas"][index]["status"] = "HARD_REJECT"
                        pipeline_state["alphas"][index]["error_message"] = f"Submission check failed: {err_detail}"
                        break
                    else:
                        log_message("INFO", f"Alpha #{index+1}: Submission checks in progress... ({poll_i+1}/{poll_limit})")
                
                if not submitted_ok and pipeline_state["alphas"][index]["status"] != "HARD_REJECT":
                    log_message("WARNING", f"Alpha #{index+1}: Submission polling timed out after {poll_limit} attempts.")
            else:
                err_msg = submit_r.text[:200]
                log_message("WARNING", f"Alpha #{index+1} submission POST failed: {err_msg}")
        
        # Always color qualifying alphas RED (SUBMITTED or SOFT_FAIL with good Sharpe)
        if alpha_id and status in ("SUBMITTED", "SOFT_FAIL"):
            try:
                color_r = robust_request(session, "PATCH", f"{WQ_ALPHAS_URL}/{alpha_id}", index=index, json={"color": "RED"}, timeout=30)
                if color_r.status_code == 200:
                    log_message("SUBMITTED", f"Alpha #{index+1} colored RED on WQ platform.")
                else:
                    log_message("WARNING", f"Alpha #{index+1} coloring failed: {color_r.text[:100]}")
            except Exception as e:
                log_message("ERROR", f"Error coloring alpha RED: {e}")

    except Exception as e:
        log_message("ERROR", f"Alpha #{index+1} metric collection failed: {e}")
        pipeline_state["alphas"][index]["status"] = "ERROR"
        pipeline_state["alphas"][index]["error_message"] = str(e)


def main():
    init_db()
    
    # Establish Session
    log_message("INFO", "Logging into WorldQuant Brain...")
    session = WQSession()
    log_message("INFO", "Session established successfully.")

    # Start Flask Server
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    log_message("INFO", "Web dashboard available at http://127.0.0.1:8000")

    # Self-ping to prevent Render free-tier spin-down (every 60 seconds)
    def self_ping_loop():
        import requests as _req
        time.sleep(15)  # wait for Flask to fully boot first
        port = int(os.environ.get("PORT", 8000))
        url = f"http://127.0.0.1:{port}/api/queue-status"
        while True:
            try:
                _req.get(url, timeout=5)
                log_message("INFO", "[KEEPALIVE] Self-ping OK — Render spin-down prevented.")
            except Exception as e:
                log_message("WARNING", f"[KEEPALIVE] Self-ping failed: {e}")
            time.sleep(60)

    ping_thread = threading.Thread(target=self_ping_loop, daemon=True)
    ping_thread.start()
    log_message("INFO", "[KEEPALIVE] Self-ping thread started (interval: 60s)")

    # Dynamic Queue Scheduler State
    scheduled_formulas = set()
    completed_formulas = set()
    futures = []

    log_message("INFO", f"Dynamic Queue Scheduler Active (concurrency limit: {MAX_CONCURRENT_SIMS})...")

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_SIMS) as executor:
        try:
            while True:
                # Poll db/simulation_queue.json for new alphas
                queue_file = Path("db/simulation_queue.json")
                if queue_file.exists():
                    try:
                        with open(queue_file, "r") as f:
                            tasks = json.load(f)
                    except Exception:
                        tasks = []
                    
                    # Detect and dynamically submit new formulas
                    for task in tasks:
                        formula = task["formula"]
                        if formula not in scheduled_formulas:
                            scheduled_formulas.add(formula)
                            idx = len(pipeline_state["alphas"])
                            
                            # Add to shared pipeline state dynamically
                            pipeline_state["alphas"].append({
                                "formula": formula,
                                "family": task["family"],
                                "hypothesis": task["hypothesis"],
                                "status": "PENDING",
                                "progress": 0,
                                "sharpe": None,
                                "fitness": None,
                                "turnover": None,
                                "error_message": None
                            })
                            
                            log_message("INFO", f"Dynamic Queue: Detected and queued new alpha #{idx+1}: {formula}")
                            
                            # Submit task to ThreadPoolExecutor
                            # Slight offset on thread execution to avoid immediate post contention
                            def make_runner(t_idx=idx, t_task=task):
                                def task_runner():
                                    time.sleep(1.0)
                                    simulate_task(t_idx, t_task, session)
                                return task_runner
                            
                            futures.append(executor.submit(make_runner(idx, task)))
                
                # Check for any completed alphas to log summaries
                for idx, alpha in enumerate(pipeline_state["alphas"]):
                    formula = alpha["formula"]
                    if formula not in completed_formulas and alpha["status"] in ("SUBMITTED", "HARD_REJECT", "SOFT_FAIL", "ERROR"):
                        completed_formulas.add(formula)
                        sharpe = f"{alpha['sharpe']:.2f}" if alpha['sharpe'] is not None else "-"
                        log_message("INFO", f"Alpha #{idx+1} finished! Status: {alpha['status']} | Sharpe: {sharpe}")

                # Update pipeline status in state
                if scheduled_formulas and len(completed_formulas) == len(scheduled_formulas):
                    pipeline_state["status"] = "COMPLETED"
                else:
                    pipeline_state["status"] = "RUNNING"
                
                # Polling interval
                time.sleep(3)
                
        except KeyboardInterrupt:
            log_message("INFO", "KeyboardInterrupt detected. Shutting down pipeline gracefully...")
            
    log_message("INFO", "Pipeline shutdown complete.")

if __name__ == "__main__":
    main()

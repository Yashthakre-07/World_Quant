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
from src.config import WQ_SIM_URL, WQ_ALPHAS_URL, DEFAULT_SIM_SETTINGS, ALPHAS_OUT_DIR, MAX_CONCURRENT_SIMS, WQ_EMAIL, DB_DIR

# Initialize Flask app
app = Flask(__name__)

# Prevent browser caching of static dashboard assets
@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

# Secure API token for the /api/queue-alpha push endpoint
# Set API_SECRET_TOKEN in Render environment variables
API_SECRET_TOKEN = os.environ.get("API_SECRET_TOKEN", "wq-default-token-change-me")

# Notification Config (WhatsApp & Telegram)
WA_PHONE = os.environ.get("WA_PHONE", "")
WA_APIKEY = os.environ.get("WA_APIKEY", "")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_whatsapp(message: str):
    """Send alert via WhatsApp (CallMeBot) and/or Telegram depending on environment variables."""
    # 1. WhatsApp Notification
    if WA_PHONE and WA_APIKEY:
        try:
            import urllib.parse
            import urllib.request
            encoded = urllib.parse.quote(message)
            url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={encoded}&apikey={WA_APIKEY}"
            urllib.request.urlopen(url, timeout=8)
        except Exception as e:
            print(f"[WA_NOTIFY] Failed to send WhatsApp alert: {e}")

    # 2. Telegram Notification
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            import urllib.parse
            import urllib.request
            encoded = urllib.parse.quote(message)
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={encoded}"
            urllib.request.urlopen(url, timeout=8)
        except Exception as e:
            print(f"[TG_NOTIFY] Failed to send Telegram alert: {e}")

# Lock to space API submissions sequentially and avoid rate limits
submission_lock = threading.Lock()
reauth_lock = threading.Lock()

# Shared Pipeline State
pipeline_state = {
    "status": "RUNNING",  # RUNNING, COMPLETED, PAUSED
    "alphas": [],
    "logs": []
}

pipeline_active = True
active_session = None

# Interactive re-authentication state
reauth_state = {
    "status": "IDLE",  # IDLE, POLLING, SUCCESS, ERROR
    "url": "",
    "error": ""
}
reauth_thread = None

def log_message(level, msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] [{level}] {msg}"
    print(full_msg)
    pipeline_state["logs"].append(full_msg)

from src.auth import set_log_callback
set_log_callback(log_message)

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
            max-height: 800px;
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
    return app.send_static_file("index.html")

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
    queue_path = DB_DIR / "simulation_queue.json"
    tasks = []
    if queue_path.exists():
        try:
            with open(queue_path, "r") as f:
                tasks = json.load(f)
        except Exception:
            tasks = []

    # 3. Read latest runs from SQLite database
    runs = {}
    db_path = DB_DIR / "alpha_vault.db"
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

    # 4. Map in-memory alphas for live progress/simulating status
    in_memory_info = {}
    for a in pipeline_state.get("alphas", []):
        f_str = a.get("formula")
        if f_str:
            in_memory_info[f_str] = {
                "status": a.get("status"),
                "progress": a.get("progress"),
                "sharpe": a.get("sharpe"),
                "fitness": a.get("fitness"),
                "turnover": a.get("turnover"),
                "error_message": a.get("error_message")
            }

    # 5. Construct live state dynamically
    alphas_state = []
    for idx, task in enumerate(tasks):
        formula = task["formula"]
        
        if formula in in_memory_info:
            run_info = in_memory_info[formula]
            status = run_info.get("status", "PENDING")
            progress = run_info.get("progress", 0)
        else:
            run_info = runs.get(formula, {})
            status = run_info.get("status", "PENDING")
            progress = 100 if status in ("SUBMITTED", "HARD_REJECT", "SOFT_FAIL", "ERROR") else 0
            
        alphas_state.append({
            "formula": formula,
            "family": task.get("family", "Unknown"),
            "hypothesis": task.get("hypothesis", ""),
            "status": status,
            "progress": progress,
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
        # Load Sai's email dynamically from sai.env to always check the correct profile!
        sai_email = ""
        sai_env_path = Path("sai.env")
        if sai_env_path.exists():
            from dotenv import dotenv_values
            sai_config = dotenv_values(sai_env_path)
            sai_email = sai_config.get("WQ_EMAIL", "")
            
        email_to_check = sai_email if sai_email else WQ_EMAIL
        safe_email = email_to_check.replace("@", "_").replace(".", "_") if email_to_check else "default"
        active_cookie_file = DB_DIR / f"session_cookies_{safe_email}.json"
        
        if active_cookie_file.exists():
            target_cookie_file = active_cookie_file
        else:
            cookie_files = list(DB_DIR.glob("session_cookies_*.json"))
            if not cookie_files:
                return jsonify({"error": "No session file found", "exp_epoch": 0})
            target_cookie_file = cookie_files[0]
            
        with open(target_cookie_file) as f:
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

@app.route("/api/reauthenticate", methods=["POST"])
def reauthenticate():
    global active_session, reauth_thread
    
    # If already polling for biometric verification, do not start a new login attempt
    if reauth_state["status"] == "POLLING":
        log_message("WARNING", "Re-authentication is already in progress. Re-using current verification URL.")
        # If running locally, open the browser tab again for convenience
        if os.getenv("RENDER") != "true" and reauth_state["url"]:
            try:
                import webbrowser
                webbrowser.open(reauth_state["url"])
            except Exception:
                pass
        return jsonify(reauth_state)
    
    # Always reset state for a fresh attempt
    reauth_state["status"] = "IDLE"
    reauth_state["url"] = ""
    reauth_state["error"] = ""
    
    try:
        from src.auth import WQSession, PersonaRequiredException
        import src.auth
        import src.config
        from dotenv import load_dotenv
        
        # Explicitly load Sai's environment variables
        sai_env_path = Path("sai.env")
        if sai_env_path.exists():
            load_dotenv(sai_env_path, override=True)
            
        # Update config and auth module variables dynamically
        src.config.WQ_EMAIL = os.getenv("WQ_EMAIL", "")
        src.config.WQ_PASSWORD = os.getenv("WQ_PASSWORD", "")
        src.auth.WQ_EMAIL = src.config.WQ_EMAIL
        src.auth.WQ_PASSWORD = src.config.WQ_PASSWORD
        
        reauth_state["status"] = "POLLING"
        reauth_state["url"] = ""
        reauth_state["error"] = ""
        
        # Instantiate in interactive mode
        sess = WQSession(interactive=True)
        
        # If it returns without exception, login was succeeded instantly via saved cookies/credentials
        active_session = sess
        reauth_state["status"] = "SUCCESS"
        return jsonify({"status": "SUCCESS", "message": "Authenticated instantly using persisted cookies!"})
        
    except PersonaRequiredException as e:
        reauth_state["status"] = "POLLING"
        reauth_state["url"] = e.url
        sess = e.session
        
        # Open web browser locally if not on Render!
        if os.getenv("RENDER") != "true":
            try:
                import webbrowser
                webbrowser.open(e.url)
            except Exception as web_err:
                log_message("WARNING", f"Failed to open browser locally: {web_err}")

        # Send the biometric verification link directly to the user's phone!
        try:
            send_whatsapp(
                f"🔐 BIOMETRIC VERIFICATION REQUIRED\n"
                f"Please open this link on your phone to complete WorldQuant verification:\n"
                f"{e.url}"
            )
        except Exception:
            pass
        
        # Poll WorldQuant for biometric confirmation in a background thread to prevent blocking
        def poll_persona():
            global active_session
            try:
                payload = e.inquiry_payload
                for attempt in range(60):  # Poll every 5s for up to 5 minutes
                    time.sleep(5)
                    p_r = sess.post("https://api.worldquantbrain.com/authentication/persona", json=payload)
                    if p_r.status_code == 201:
                        sess.login_expired = False
                        sess.save_persisted_cookies()
                        active_session = sess
                        reauth_state["status"] = "SUCCESS"
                        log_message("INFO", "Interactive re-authentication completed successfully!")
                        # Send restoration alert to phone
                        try:
                            send_whatsapp("✅ SESSION RESTORED\nBiometric verification complete! WorldQuant Brain session is live and simulations are resuming.")
                        except Exception:
                            pass
                        return
                
                reauth_state["status"] = "ERROR"
                reauth_state["error"] = "Biometric verification timed out. Please try again."
                log_message("ERROR", "Interactive re-authentication timed out.")
            except Exception as err:
                reauth_state["status"] = "ERROR"
                reauth_state["error"] = str(err)
                log_message("ERROR", f"Interactive re-authentication background error: {err}")
                
        reauth_thread = threading.Thread(target=poll_persona, daemon=True)
        reauth_thread.start()
        
        return jsonify(reauth_state)
        
    except Exception as e:
        reauth_state["status"] = "ERROR"
        reauth_state["error"] = str(e)
        return jsonify({"status": "ERROR", "error": str(e)})

@app.route("/api/reauth-status", methods=["GET"])
def reauth_status():
    return jsonify(reauth_state)

@app.route("/api/queue-alpha", methods=["POST"])
def queue_alpha():
    """Secure endpoint: push new alphas from API client to review inbox.
    Requires Bearer token matching API_SECRET_TOKEN env var.
    Body: [{"formula": "...", "family": "...", "hypothesis": "...", "settings": {...}}]
    """
    # --- Auth check ---
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    is_same_origin = request.referrer and request.referrer.startswith(request.url_root)
    if not is_same_origin and token != API_SECRET_TOKEN:
        return jsonify({"error": "Unauthorized", "hint": "Provide valid Bearer token"}), 401

    # --- Parse body ---
    try:
        data = request.get_json(force=True)
        if not isinstance(data, list):
            data = [data]  # Accept single object or array
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    # --- Validate and append each alpha to inbox_queue ---
    added = []
    skipped = []
    inbox_path = DB_DIR / "inbox_queue.json"
    queue_path = DB_DIR / "simulation_queue.json"

    # Load current inbox
    existing_inbox = []
    if inbox_path.exists():
        try:
            with open(inbox_path) as f:
                existing_inbox = json.load(f)
        except Exception:
            existing_inbox = []

    # Load current queue from disk
    existing_queue = []
    if queue_path.exists():
        try:
            with open(queue_path) as f:
                existing_queue = json.load(f)
        except Exception:
            existing_queue = []

    existing_formulas = {a.get("formula", "").strip() for a in existing_inbox}
    existing_formulas.update(a.get("formula", "").strip() for a in existing_queue)
    # Also skip formulas already in memory
    existing_formulas.update(a["formula"].strip() for a in pipeline_state["alphas"])

    for item in data:
        formula = item.get("formula", "").strip()
        if not formula:
            skipped.append({"reason": "Missing formula", "item": item})
            continue
        if formula in existing_formulas:
            skipped.append({"reason": "Already queued or in inbox", "formula": formula})
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

        # Append to disk inbox
        existing_inbox.append(task)
        existing_formulas.add(formula)
        added.append(formula)
        log_message("INFO", f"[API] Received alpha into review inbox: {formula[:80]}...")

    # Save updated inbox to disk
    inbox_path.parent.mkdir(exist_ok=True)
    with open(inbox_path, "w") as f:
        json.dump(existing_inbox, f, indent=2)

    return jsonify({
        "status": "ok",
        "added": len(added),
        "skipped": len(skipped),
        "added_formulas": added,
        "skipped_details": skipped
    })

@app.route("/api/queue-alpha-direct", methods=["POST"])
def queue_alpha_direct():
    """Secure direct manual entry: bypassed review inbox."""
    is_same_origin = request.referrer and request.referrer.startswith(request.url_root)
    if not is_same_origin:
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        item = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400
        
    formula = item.get("formula", "").strip()
    if not formula:
        return jsonify({"error": "Missing formula"}), 400
        
    queue_path = DB_DIR / "simulation_queue.json"
    
    # Load current active queue
    active_queue = []
    if queue_path.exists():
        try:
            with open(queue_path, "r") as f:
                active_queue = json.load(f)
        except Exception:
            pass
            
    existing_formulas = {a.get("formula", "").strip() for a in active_queue}
    existing_formulas.update(a["formula"].strip() for a in pipeline_state["alphas"])
    
    if formula in existing_formulas:
        return jsonify({"error": "Already queued or simulating"}), 400
        
    task = {
        "family": item.get("family", "Manual Entry"),
        "hypothesis": item.get("hypothesis", "Direct manual entry"),
        "formula": formula,
        "settings": item.get("settings", {
            "decay": 5, "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000", "truncation": 0.08
        })
    }
    
    active_queue.append(task)
    
    queue_path.parent.mkdir(exist_ok=True)
    with open(queue_path, "w") as f:
        json.dump(active_queue, f, indent=2)
        
    log_message("INFO", f"[INJECTOR] Manually queued alpha directly: {formula[:80]}...")
    return jsonify({"status": "ok"})

@app.route("/api/inbox-alphas", methods=["GET"])
def get_inbox_alphas():
    inbox_path = Path("db") / "inbox_queue.json"
    alphas = []
    if inbox_path.exists():
        try:
            with open(inbox_path, "r") as f:
                alphas = json.load(f)
        except Exception:
            alphas = []
    return jsonify(alphas)

@app.route("/api/inject-inbox", methods=["POST"])
def inject_inbox():
    try:
        data = request.get_json(force=True)
    except Exception:
        data = {}
        
    inbox_path = DB_DIR / "inbox_queue.json"
    queue_path = DB_DIR / "simulation_queue.json"
    
    inbox_alphas = []
    if inbox_path.exists():
        try:
            with open(inbox_path, "r") as f:
                inbox_alphas = json.load(f)
        except Exception:
            pass
            
    # Load current active queue
    active_queue = []
    if queue_path.exists():
        try:
            with open(queue_path, "r") as f:
                active_queue = json.load(f)
        except Exception:
            pass
            
    existing_formulas = {a.get("formula", "").strip() for a in active_queue}
    
    # Filter which ones to inject
    target_formulas = data.get("formulas", [])
    inject_all = data.get("all", False)
    
    to_inject = []
    remaining_inbox = []
    
    for item in inbox_alphas:
        formula = item.get("formula", "").strip()
        if inject_all or (formula in target_formulas):
            if formula and formula not in existing_formulas:
                to_inject.append(item)
                existing_formulas.add(formula)
        else:
            remaining_inbox.append(item)
            
    if to_inject:
        active_queue.extend(to_inject)
        # Save updated active queue to disk
        queue_path.parent.mkdir(exist_ok=True)
        with open(queue_path, "w") as f:
            json.dump(active_queue, f, indent=2)
            
        # Log to system console
        for item in to_inject:
            log_message("INFO", f"[INJECTOR] Pushed alpha to backtest queue: {item['formula'][:80]}...")
            
    # Save remaining in inbox
    with open(inbox_path, "w") as f:
        json.dump(remaining_inbox, f, indent=2)
        
    return jsonify({
        "status": "ok",
        "injected_count": len(to_inject),
        "remaining_count": len(remaining_inbox)
    })

@app.route("/api/clear-inbox", methods=["POST"])
def clear_inbox():
    inbox_path = DB_DIR / "inbox_queue.json"
    try:
        with open(inbox_path, "w") as f:
            json.dump([], f, indent=2)
        log_message("INFO", "[API] Inbox queue cleared by operator.")
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/clear-queue", methods=["POST"])
def clear_queue():
    """Secure endpoint: clear the entire queue on disk."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    is_same_origin = request.referrer and request.referrer.startswith(request.url_root)
    if not is_same_origin and token != API_SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    queue_path = DB_DIR / "simulation_queue.json"
    inbox_path = DB_DIR / "inbox_queue.json"
    try:
        # Clear queues on disk
        with open(queue_path, "w") as f:
            json.dump([], f, indent=2)
        with open(inbox_path, "w") as f:
            json.dump([], f, indent=2)
            
        # Clear dynamic queue in memory
        global pipeline_state, pipeline_active
        pipeline_state["alphas"] = []
        pipeline_state["status"] = "COMPLETED"
        pipeline_active = False
        
        log_message("INFO", "[API] Dynamic Queue & Inbox cleared and memory state reset via API command.")
        return jsonify({"status": "ok", "message": "Queue and memory state cleared successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/purge-vault", methods=["POST"])
def purge_vault():
    """Secure endpoint: completely clears the database runs and local JSON files on Render."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    is_same_origin = request.referrer and request.referrer.startswith(request.url_root)
    if not is_same_origin and token != API_SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    db_path = DB_DIR / "alpha_vault.db"
    cleared_db = False
    if db_path.exists():
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("DELETE FROM submitted_alphas")
            cursor.execute("DELETE FROM alpha_runs")
            conn.commit()
            conn.close()
            cleared_db = True
        except Exception as e:
            log_message("WARNING", f"[API] Failed to clear SQLite vault database: {e}")

    # Clear JSON files
    cleared_files = 0
    try:
        out_dir = Path(ALPHAS_OUT_DIR)
        if out_dir.exists():
            for af in out_dir.glob("alpha_*.json"):
                try:
                    af.unlink()
                    cleared_files += 1
                except Exception:
                    pass
    except Exception as e:
        log_message("WARNING", f"[API] Failed to clear alphas directory: {e}")

    log_message("INFO", f"[API] Vault purged via API. DB Cleared: {cleared_db}, Files deleted: {cleared_files}")
    return jsonify({
        "status": "ok",
        "db_cleared": cleared_db,
        "files_deleted": cleared_files,
        "message": "Vault successfully purged."
    })

@app.route("/api/clean-queue", methods=["POST"])
def clean_queue():
    """
    Secure endpoint: clean dynamic queue by:
      1. Logging any requested failed/rejected alphas directly into the SQLite database.
      2. Scanning the queue for any formulas present in the database as failed/rejected/error, and removing them.
      3. Cleaning them from the in-memory list to instantly update the UI.
    """
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    is_same_origin = request.referrer and request.referrer.startswith(request.url_root)
    if not is_same_origin and token != API_SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    req_data = {}
    try:
        if request.data:
            req_data = request.get_json(force=True) or {}
    except Exception:
        pass

    # 1. Store newly passed failed alphas into SQLite database
    failed_injected = req_data.get("failed_alphas", [])
    if isinstance(failed_injected, list) and len(failed_injected) > 0:
        for item in failed_injected:
            formula = item.get("formula", "").strip()
            if not formula:
                continue
            
            # If not already simulated/stored, insert into database
            if not check_already_simulated(formula):
                run_uuid = str(uuid.uuid4())[:8]
                try:
                    save_alpha_run({
                        "run_id": run_uuid,
                        "family": item.get("family", "Manual Failure Check"),
                        "hypothesis": item.get("hypothesis", "Failed/Rejected Alpha Injected via API"),
                        "formula": formula,
                        "region": "USA", "universe": "TOP3000", "neutralization": "SUBINDUSTRY",
                        "decay": 6, "truncation": 0.08, "delay": 1,
                        "sharpe": item.get("sharpe"), "fitness": item.get("fitness"), "turnover": item.get("turnover"),
                        "checks_passed": 0, "weight_check": "FAIL", "sub_sharpe": -1.0,
                        "status": item.get("status", "HARD_REJECT"),
                        "alpha_link": None, "sim_link": None,
                        "error_message": item.get("error_message", "Injected Failure"),
                        "llm_model": "gemini-1.5-flash", "parent_id": None
                    })
                    log_message("INFO", f"[API] Logged custom failure directly to database: {formula[:50]}...")
                except Exception as e:
                    log_message("WARNING", f"[API] Failed to write custom failure to DB: {e}")

    # 2. Clean queue of disk
    queue_path = DB_DIR / "simulation_queue.json"
    if not queue_path.exists():
        return jsonify({"status": "ok", "removed_count": 0, "message": "No queue file found to clean."})

    try:
        with open(queue_path, "r") as f:
            queue_tasks = json.load(f)
    except Exception as e:
        return jsonify({"error": f"Failed to read queue: {e}"}), 500

    cleaned_tasks = []
    removed_formulas = []

    for task in queue_tasks:
        formula = task.get("formula", "").strip()
        if not formula:
            continue
        
        cached = check_already_simulated(formula)
        if cached and cached.get("status") in ("HARD_REJECT", "SOFT_FAIL", "ERROR"):
            removed_formulas.append(formula)
            log_message("INFO", f"[API] Removing failed/rejected alpha from dynamic queue: {formula[:50]}...")
        else:
            cleaned_tasks.append(task)

    try:
        with open(queue_path, "w") as f:
            json.dump(cleaned_tasks, f, indent=2)
            
        # 3. Clean from active in-memory list (pipeline_state["alphas"]) to update UI instantly
        pipeline_state["alphas"] = [a for a in pipeline_state["alphas"] if a.get("formula") not in removed_formulas]
        
        return jsonify({
            "status": "ok",
            "removed_count": len(removed_formulas),
            "removed_formulas": removed_formulas,
            "remaining_queue_count": len(cleaned_tasks)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to save cleaned queue: {e}"}), 500

@app.route("/api/stop-pipeline", methods=["POST"])
def stop_pipeline():
    """Secure endpoint: pauses the pipeline execution loop."""
    global pipeline_active
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    if token != API_SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    
    pipeline_active = False
    pipeline_state["status"] = "PAUSED"
    log_message("WARNING", "[API] Pipeline has been PAUSED via remote desktop call.")
    return jsonify({"status": "ok", "pipeline_active": False, "message": "Pipeline paused."})

@app.route("/api/start-pipeline", methods=["POST"])
def start_pipeline():
    """Secure endpoint: resumes/starts the pipeline execution loop."""
    global pipeline_active
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    if token != API_SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    
    pipeline_active = True
    pipeline_state["status"] = "RUNNING"
    log_message("INFO", "[API] Pipeline has been RESUMED/STARTED via remote desktop call.")
    return jsonify({"status": "ok", "pipeline_active": True, "message": "Pipeline active."})

@app.route("/api/reset-state", methods=["POST"])
def reset_state():
    """Secure endpoint: fully clears in-memory pipeline_state alphas list.
    This forces the background scheduler to re-read all formulas from disk 
    on the next poll and re-schedule every formula as if fresh — solving the
    scheduled_formulas dedup-skip problem when the queue is replaced."""
    global pipeline_active
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    if token != API_SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    prev_count = len(pipeline_state["alphas"])
    pipeline_state["alphas"] = []
    pipeline_state["status"] = "RUNNING"
    pipeline_active = True
    log_message("INFO", f"[API] Pipeline state RESET — cleared {prev_count} in-memory alphas. Scheduler will re-discover all queue formulas.")
    return jsonify({"status": "ok", "cleared_alphas": prev_count, "message": "Pipeline state reset. All queue formulas will be re-scheduled."})

@app.route("/api/alphas", methods=["GET"])
def list_alphas():
    """Secure endpoint: lists all successfully generated alpha files on Render."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    if token != API_SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        out_dir = Path(ALPHAS_OUT_DIR)
        if not out_dir.exists():
            return jsonify({"alphas": []})
        
        alpha_files = list(out_dir.glob("alpha_*.json"))
        results = []
        for af in alpha_files:
            try:
                with open(af, "r") as f:
                    data = json.load(f)
                results.append({
                    "alpha_id": data.get("alpha_id"),
                    "family": data.get("family"),
                    "status": data.get("status"),
                    "sharpe": data.get("sharpe"),
                    "fitness": data.get("fitness"),
                    "turnover": data.get("turnover"),
                    "filename": af.name
                })
            except Exception:
                results.append({"filename": af.name, "error": "Unparseable"})
        return jsonify({"alphas": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/alpha/<alpha_id>", methods=["GET"])
def fetch_alpha(alpha_id):
    """Secure endpoint: returns the complete raw JSON data of a specific alpha."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    if token != API_SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        out_dir = Path(ALPHAS_OUT_DIR)
        alpha_file = out_dir / f"alpha_{alpha_id}.json"
        if not alpha_file.exists():
            return jsonify({"error": f"Alpha {alpha_id} not found."}), 404
        
        with open(alpha_file, "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/overwrite-queue", methods=["POST"])
def overwrite_queue():
    """Secure endpoint: overwrite the queue entirely with new alphas."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    if token != API_SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json(force=True)
        if not isinstance(data, list):
            data = [data]
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    queue_path = Path("db") / "simulation_queue.json"
    new_queue = []
    for item in data:
        formula = item.get("formula", "").strip()
        if not formula:
            continue
        new_queue.append({
            "family": item.get("family", "API Overwritten"),
            "hypothesis": item.get("hypothesis", "Injected via secure overwrite API"),
            "formula": formula,
            "settings": item.get("settings", {
                "decay": 5, "neutralization": "SUBINDUSTRY",
                "universe": "TOP3000", "truncation": 0.08
            })
        })

    try:
        queue_path.parent.mkdir(exist_ok=True)
        with open(queue_path, "w") as f:
            json.dump(new_queue, f, indent=2)
        log_message("INFO", f"[API] Dynamic Queue overwritten with {len(new_queue)} alphas.")
        return jsonify({"status": "ok", "overwritten_count": len(new_queue)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@app.route("/api/stats", methods=["GET"])
def get_api_stats():
    import sqlite3
    db_path = DB_DIR / "alpha_vault.db"
    
    total_runs = 0
    total_submissions = 0
    best_sharpe = 0.0
    best_fitness = 0.0
    families = []
    submitted_list = []
    
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Total runs
            cursor.execute("SELECT COUNT(*) FROM alpha_runs")
            total_runs = cursor.fetchone()[0] or 0
            
            # Total submissions
            cursor.execute("SELECT COUNT(*) FROM alpha_runs WHERE status = 'SUBMITTED'")
            total_submissions = cursor.fetchone()[0] or 0
            
            # Best Sharpe
            cursor.execute("SELECT MAX(sharpe) FROM alpha_runs")
            best_sharpe = cursor.fetchone()[0] or 0.0
            
            # Best Fitness
            cursor.execute("SELECT MAX(fitness) FROM alpha_runs")
            best_fitness = cursor.fetchone()[0] or 0.0
            
            # Families breakdown using the view or fallback query
            try:
                cursor.execute("SELECT family, total_runs, submitted, success_rate FROM family_stats")
                for row in cursor.fetchall():
                    families.append({
                        "family": row[0],
                        "total_runs": row[1],
                        "submitted": row[2],
                        "success_rate": row[3]
                    })
            except Exception:
                cursor.execute("""
                SELECT family, COUNT(*), SUM(CASE WHEN status='SUBMITTED' THEN 1 ELSE 0 END)
                FROM alpha_runs GROUP BY family
                """)
                for row in cursor.fetchall():
                    success_rate = round(100.0 * row[2] / row[1], 1) if row[1] > 0 else 0.0
                    families.append({
                        "family": row[0],
                        "total_runs": row[1],
                        "submitted": row[2],
                        "success_rate": success_rate
                    })
            
            # Submitted List from submitted_alphas joined with alpha_runs
            try:
                cursor.execute("""
                SELECT s.alpha_id, r.sharpe, r.fitness, r.turnover, r.alpha_link
                FROM submitted_alphas s
                JOIN alpha_runs r ON s.alpha_run_id = r.id
                ORDER BY s.id DESC
                """)
                for row in cursor.fetchall():
                    submitted_list.append({
                        "alpha_id": row[0],
                        "sharpe": row[1] or 0.0,
                        "fitness": row[2] or 0.0,
                        "turnover": row[3] or 0.0,
                        "alpha_link": row[4] or "#"
                    })
            except Exception:
                # Fallback to direct alpha_runs
                cursor.execute("""
                SELECT run_id, sharpe, fitness, turnover, alpha_link
                FROM alpha_runs
                WHERE status = 'SUBMITTED'
                ORDER BY id DESC
                """)
                for row in cursor.fetchall():
                    submitted_list.append({
                        "alpha_id": row[0],
                        "sharpe": row[1] or 0.0,
                        "fitness": row[2] or 0.0,
                        "turnover": row[3] or 0.0,
                        "alpha_link": row[4] or "#"
                    })
            
            # All Alphas in Vault - Merge JSON files and database runs
            vault_alphas_dict = {}
            
            # 1. Load from alphas/ output directory
            try:
                out_dir = Path(ALPHAS_OUT_DIR)
                if out_dir.exists():
                    for af in out_dir.glob("alpha_*.json"):
                        try:
                            with open(af, "r") as f:
                                data = json.load(f)
                            alpha_id = data.get("alpha_id") or af.stem.replace("alpha_", "")
                            vault_alphas_dict[alpha_id] = {
                                "alpha_id": alpha_id,
                                "family": data.get("family") or "Unknown",
                                "formula": data.get("formula") or "",
                                "sharpe": data.get("sharpe") or 0.0,
                                "fitness": data.get("fitness") or 0.0,
                                "turnover": data.get("turnover") or 0.0,
                                "status": data.get("status") or "SUBMITTED",
                                "error_message": data.get("error_message") or "",
                                "alpha_link": data.get("alpha_link") or "#",
                                "created_at": ""
                            }
                        except Exception:
                            pass
            except Exception as e:
                print(f"[API_STATS] Error reading alphas directory: {e}")

            # 2. Merge with alpha_runs SQLite database (gives dynamic/failed runs too)
            try:
                cursor.execute("""
                SELECT run_id, family, formula, sharpe, fitness, turnover, status, error_message, alpha_link, timestamp
                FROM alpha_runs
                """)
                for row in cursor.fetchall():
                    run_id = row[0]
                    db_status = row[6] or "PENDING"
                    if run_id in vault_alphas_dict:
                        existing = vault_alphas_dict[run_id]
                        # If database status is SUBMITTED, prioritize database links/stats
                        if db_status == "SUBMITTED" or existing.get("status") != "SUBMITTED":
                            existing["status"] = db_status
                            if row[3] is not None: existing["sharpe"] = row[3]
                            if row[4] is not None: existing["fitness"] = row[4]
                            if row[5] is not None: existing["turnover"] = row[5]
                            if row[8]: existing["alpha_link"] = row[8]
                            if row[7]: existing["error_message"] = row[7]
                    else:
                        vault_alphas_dict[run_id] = {
                            "alpha_id": run_id,
                            "family": row[1] or "Unknown",
                            "formula": row[2] or "",
                            "sharpe": row[3] or 0.0,
                            "fitness": row[4] or 0.0,
                            "turnover": row[5] or 0.0,
                            "status": db_status,
                            "error_message": row[7] or "",
                            "alpha_link": row[8] or "#",
                            "created_at": row[9] or ""
                        }
            except Exception as e:
                print(f"[API_STATS] Error querying vault_alphas database: {e}")
                
            vault_alphas = list(vault_alphas_dict.values())
            # Sort by alpha_id desc to show newest/highest IDs first
            vault_alphas.sort(key=lambda x: x.get("alpha_id", ""), reverse=True)
            
            conn.close()
        except Exception as e:
            print(f"[API_STATS] Error querying DB: {e}")
            
    return jsonify({
        "total_runs": total_runs,
        "total_submissions": total_submissions,
        "best_sharpe": best_sharpe,
        "best_fitness": best_fitness,
        "families": families,
        "submitted_list": submitted_list,
        "vault_alphas": vault_alphas
    })

# Shared state for automation platform
sweep_state = {
    "status": "IDLE",  # IDLE, RUNNING, SUCCESS, ERROR
    "message": "",
    "found": 0,
    "added": 0
}

submission_state = {
    "status": "IDLE",  # IDLE, RUNNING, SUCCESS, ERROR
    "total": 0,
    "current_index": 0,
    "current_alpha_id": "",
    "success_count": 0,
    "fail_count": 0,
    "message": ""
}

def bg_sweep_task():
    global active_session, sweep_state
    sweep_state["status"] = "RUNNING"
    sweep_state["message"] = "Authenticating..."
    sweep_state["found"] = 0
    sweep_state["added"] = 0
    
    if active_session is None:
        sweep_state["status"] = "ERROR"
        sweep_state["message"] = "No active session. Please click 'Re-auth Session' to complete login."
        return
        
    try:
        import sqlite3
        from src.database import DB_PATH, upsert_all_alphas, add_to_queue
        
        url = "https://api.worldquantbrain.com/users/self/alphas"
        params = {"limit": 100}
        alphas = []
        sweep_state["message"] = "Fetching alphas from WorldQuant..."
        
        while url:
            r = active_session.get(url, params=params, timeout=30)
            if r.status_code != 200:
                raise ValueError(f"Failed to fetch alphas from WQ: HTTP {r.status_code}")
            res = r.json()
            alphas.extend(res.get("results", []))
            
            url = None
            for link in res.get("links", []):
                if link.get("rel") == "next":
                    url = link.get("href")
                    params = None
                    break
        
        sweep_state["message"] = f"Processing {len(alphas)} alphas..."
        
        # Process and upsert to database
        processed_alphas = []
        for a in alphas:
            alpha_id = a.get("id")
            formula = a.get("regular", {}).get("code", "")
            metrics = a.get("is", {})
            sharpe = metrics.get("sharpe")
            fitness = metrics.get("fitness")
            turnover = metrics.get("turnover", 0.0) * 100.0 if metrics.get("turnover") is not None else 0.0
            
            processed_alphas.append({
                "alpha_id": alpha_id,
                "formula": formula,
                "sharpe": sharpe,
                "fitness": fitness,
                "turnover": turnover
            })
            
        upsert_all_alphas(processed_alphas)
        
        # Load persistent statuses
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT alpha_id FROM rejected_alphas")
        yellow_ids = {row[0] for row in cursor.fetchall()}
        cursor.execute("SELECT alpha_id FROM submitted_alphas")
        green_ids = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        candidates_to_queue = []
        for a in alphas:
            alpha_id = a.get("id")
            if alpha_id in yellow_ids or alpha_id in green_ids:
                continue
                
            if a.get("status") != "UNSUBMITTED":
                continue
                
            metrics = a.get("is", {})
            sharpe = metrics.get("sharpe")
            fitness = metrics.get("fitness")
            
            # Check weight concentration
            weight_pass = True
            checks = metrics.get("checks", [])
            for check in checks:
                if check.get("name") == "CONCENTRATED_WEIGHT" and check.get("result") == "FAIL":
                    weight_pass = False
                    
            if (sharpe is not None and sharpe >= 1.5) and \
               (fitness is not None and fitness >= 1.0) and \
               weight_pass:
                candidates_to_queue.append(alpha_id)
                
        if candidates_to_queue:
            add_to_queue(candidates_to_queue)
            
        sweep_state["status"] = "SUCCESS"
        sweep_state["message"] = f"Scan complete. Queued {len(candidates_to_queue)} qualifying submittable alphas."
        sweep_state["found"] = len(candidates_to_queue)
        log_message("INFO", f"[SCANNER] Scan complete. Found {len(candidates_to_queue)} qualifying submittable alphas.")
        
    except Exception as e:
        sweep_state["status"] = "ERROR"
        sweep_state["message"] = f"Scan failed: {str(e)}"
        log_message("ERROR", f"[SCANNER] Sweep failed: {e}")

def bg_submission_task(alpha_ids):
    global active_session, submission_state
    submission_state["status"] = "RUNNING"
    submission_state["total"] = len(alpha_ids)
    submission_state["current_index"] = 0
    submission_state["success_count"] = 0
    submission_state["fail_count"] = 0
    submission_state["message"] = "Starting submission queue..."
    
    if active_session is None:
        submission_state["status"] = "ERROR"
        submission_state["message"] = "No active session. Please authenticate first."
        return
        
    from src.client import WQClient
    from src.database import mark_alpha_green, mark_alpha_yellow, mark_alpha_red
    
    client = WQClient(active_session)
    
    for idx, alpha_id in enumerate(alpha_ids):
        submission_state["current_index"] = idx + 1
        submission_state["current_alpha_id"] = alpha_id
        submission_state["message"] = f"Submitting alpha {alpha_id} ({idx+1}/{len(alpha_ids)})..."
        log_message("INFO", f"[SUBMITTER] [{idx+1}/{len(alpha_ids)}] Submitting Alpha ID: {alpha_id}")
        
        try:
            res = client.submit_alpha(alpha_id)
            if res.get("success"):
                log_message("SUBMITTED", f"Alpha {alpha_id} submitted successfully!")
                submission_state["success_count"] += 1
                
                # Color GREEN on platform
                try:
                    color_r = active_session.patch(f"https://api.worldquantbrain.com/alphas/{alpha_id}", json={"color": "GREEN"}, timeout=15)
                    if color_r.status_code == 200:
                        log_message("INFO", f"Colored GREEN on platform successfully.")
                    else:
                        log_message("WARNING", f"Failed to color GREEN on platform: {color_r.text}")
                except Exception as e:
                    log_message("WARNING", f"Error coloring GREEN: {e}")
                    
                mark_alpha_green(alpha_id)
            else:
                details = res.get("details", "")
                log_message("ERROR", f"Alpha {alpha_id} submission failed: {details}")
                submission_state["fail_count"] += 1
                
                # If rejection is correlation / failure check
                is_hard_reject = False
                if "SELF_CORRELATION" in details or "PROD_CORRELATION" in details or "FAIL" in details or "correlation" in details.lower():
                    is_hard_reject = True
                    
                if is_hard_reject:
                    log_message("ERROR", f"Alpha {alpha_id} permanently rejected. Marking YELLOW.")
                    try:
                        color_r = active_session.patch(f"https://api.worldquantbrain.com/alphas/{alpha_id}", json={"color": "YELLOW"}, timeout=15)
                        if color_r.status_code == 200:
                            log_message("INFO", f"Colored YELLOW on platform successfully.")
                        else:
                            log_message("WARNING", f"Failed to color YELLOW on platform: {color_r.text}")
                    except Exception as e:
                        log_message("WARNING", f"Error coloring YELLOW: {e}")
                        
                    mark_alpha_yellow(alpha_id, reason=details)
                else:
                    log_message("WARNING", f"Alpha {alpha_id} temporary failure. Marking RED for retry.")
                    mark_alpha_red(alpha_id)
                    
        except Exception as e:
            log_message("ERROR", f"Error submitting alpha {alpha_id}: {e}")
            submission_state["fail_count"] += 1
            mark_alpha_red(alpha_id)
            
        # Delay between sequential submissions to respect rate limits
        if idx < len(alpha_ids) - 1:
            time.sleep(10)
            
    submission_state["status"] = "SUCCESS"
    submission_state["message"] = f"Batch submission finished. Success: {submission_state['success_count']}, Failed: {submission_state['fail_count']}"
    submission_state["current_alpha_id"] = ""
    log_message("INFO", f"[SUBMITTER] Batch submission complete. Success: {submission_state['success_count']}, Failed: {submission_state['fail_count']}")

@app.route("/api/submission-queue", methods=["GET"])
def get_submission_queue():
    from src.database import get_queue_alphas
    try:
        return jsonify(get_queue_alphas())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sweep-platform-alphas", methods=["POST"])
def sweep_platform_alphas():
    global sweep_state
    if sweep_state["status"] == "RUNNING":
        return jsonify({"status": "error", "message": "Search is already running."}), 400
        
    t = threading.Thread(target=bg_sweep_task, daemon=True)
    t.start()
    return jsonify({"status": "success", "message": "Search scanning started."})

@app.route("/api/sweep-status", methods=["GET"])
def get_sweep_status():
    return jsonify(sweep_state)

@app.route("/api/submit-alphas", methods=["POST"])
def submit_alphas():
    global submission_state
    if submission_state["status"] == "RUNNING":
        return jsonify({"status": "error", "message": "A submission process is already active."}), 400
        
    data = request.json or {}
    alpha_ids = data.get("alpha_ids", [])
    if not alpha_ids:
        return jsonify({"status": "error", "message": "No alpha IDs provided."}), 400
        
    t = threading.Thread(target=bg_submission_task, args=(alpha_ids,), daemon=True)
    t.start()
    return jsonify({"status": "success", "message": "Submission process started."})

@app.route("/api/submission-status", methods=["GET"])
def get_submission_status():
    return jsonify(submission_state)

@app.route("/api/yellow-alphas", methods=["GET"])
def get_yellow_alphas():
    from src.database import get_failed_yellow_alphas
    try:
        return jsonify(get_failed_yellow_alphas())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/submitted-alphas", methods=["GET"])
def get_submitted_alphas():
    from src.database import get_submitted_green_alphas
    try:
        return jsonify(get_submitted_green_alphas())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/platform-stats", methods=["GET"])
def get_platform_stats():
    import sqlite3
    from src.database import DB_PATH
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM queue")
        queue_count = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM rejected_alphas")
        yellow_count = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM submitted_alphas")
        green_count = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM all_alphas")
        total_count = cursor.fetchone()[0] or 0
        
        conn.close()
        return jsonify({
            "queue_count": queue_count,
            "yellow_count": yellow_count,
            "green_count": green_count,
            "total_count": total_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/logs/stream")
def stream_logs():
    from flask import Response
    def event_stream():
        import re
        log_pattern = re.compile(r"^\[(.*?)\] \[(.*?)\] (.*)$")
        
        # Send initial logs first (up to last 100)
        current_logs = pipeline_state.get("logs", [])
        start_idx = max(0, len(current_logs) - 100)
        for i in range(start_idx, len(current_logs)):
            raw_log = current_logs[i]
            match = log_pattern.match(raw_log)
            if match:
                ts, level, msg = match.groups()
            else:
                ts, msg = "", raw_log
            
            payload = {
                "message": raw_log,
                "timestamp": ts
            }
            yield f"data: {json.dumps(payload)}\n\n"
        
        last_idx = len(current_logs)
        
        # Continuous polling loop for new logs
        while True:
            time.sleep(0.5)
            current_logs = pipeline_state.get("logs", [])
            if last_idx < len(current_logs):
                for i in range(last_idx, len(current_logs)):
                    raw_log = current_logs[i]
                    match = log_pattern.match(raw_log)
                    if match:
                        ts, level, msg = match.groups()
                    else:
                        ts, msg = "", raw_log
                    
                    payload = {
                        "message": raw_log,
                        "timestamp": ts
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
                last_idx = len(current_logs)
    
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/api/state/stream")
def stream_state():
    from flask import Response
    def event_stream():
        last_status = None
        while True:
            status = pipeline_state.get("status", "INACTIVE")
            # Map simple statuses to agent statuses
            agent_status = "AGENT RUNNING"
            if status == "PAUSED":
                agent_status = "AGENT PAUSED"
            elif status == "COMPLETED":
                agent_status = "AGENT COMPLETED"
            elif status == "INACTIVE":
                agent_status = "AGENT INACTIVE"
            
            # Send status update if it changed
            if agent_status != last_status:
                payload = {"status": agent_status}
                yield f"data: {json.dumps(payload)}\n\n"
                last_status = agent_status
            time.sleep(1.0)
            
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/api/agent/start", methods=["POST"])
def agent_start():
    global pipeline_active
    pipeline_active = True
    pipeline_state["status"] = "RUNNING"
    log_message("INFO", "[SYSTEM] Agent booted via web console command.")
    return jsonify({"status": "ok", "pipeline_active": True})

@app.route("/api/agent/stop", methods=["POST"])
def agent_stop():
    global pipeline_active
    pipeline_active = False
    pipeline_state["status"] = "PAUSED"
    log_message("WARNING", "[SYSTEM] Agent paused via web console command.")
    return jsonify({"status": "ok", "pipeline_active": False})

def run_flask():
    # Run Flask server — binds to 0.0.0.0 on Render, falls back to 8000 locally
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0" if os.environ.get("RENDER") else "127.0.0.1"
    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)

def robust_request(session, method, url, index=None, **kwargs):
    """Sends an API request, automatically retries on network drop, and self-heals by logging back in on HTTP 401."""
    import requests
    global active_session
    while True:
        # Wait if active_session is None, rate-limiting the logs to avoid spamming
        last_log_time = 0
        while active_session is None:
            now = time.time()
            if now - last_log_time > 60:
                lbl = f"Alpha #{index+1}: " if index is not None else ""
                log_message("WARNING", f"{lbl}Waiting for WorldQuant Brain session to be authenticated...")
                last_log_time = now
            time.sleep(5)
            
        current_session = active_session
        try:
            if 'timeout' not in kwargs:
                kwargs['timeout'] = 30
            r = current_session.request(method, url, **kwargs)
            if r.status_code == 401:
                lbl = f"Alpha #{index+1}: " if index is not None else ""
                log_message("WARNING", f"{lbl}Session expired (HTTP 401). Attempting automatic re-authentication...")
                with reauth_lock:
                    # Check if session was already updated or cleared (failed re-auth) by another thread
                    if active_session is None or active_session != current_session:
                        continue
                        
                    # Double check if another concurrent thread has already completed the re-authentication
                    try:
                        verify = current_session.get("https://api.worldquantbrain.com/users/self", timeout=15)
                        if verify.status_code == 200:
                            log_message("INFO", f"{lbl}Session already successfully re-authenticated by another thread. Retrying request...")
                            continue
                    except Exception:
                        pass
                    
                    try:
                        current_session.authenticate()
                        log_message("INFO", f"{lbl}Automatic re-authentication successful! Retrying request...")
                        continue
                    except Exception as auth_err:
                        log_message("ERROR", f"{lbl}Automatic re-authentication failed: {auth_err}")
                        # Clear active_session to force all threads to wait and prevent spamming login attempts
                        active_session = None
                        # Send notification to phone
                        try:
                            send_whatsapp(
                                f"⚠️ SESSION EXPIRED\n"
                                f"Automatic login failed for {os.getenv('WQ_EMAIL', WQ_EMAIL)}: {auth_err}\n"
                                f"Please open the dashboard and click '🔑 Re-auth Session' to complete biometric/persona verification!"
                            )
                        except Exception:
                            pass
                        # Fall through to return the raw 401 to let the caller manage/fail as backup
                        return r
            return r
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ChunkedEncodingError) as e:
            lbl = f"Alpha #{index+1}: " if index is not None else ""
            log_message("WARNING", f"{lbl}Network connection dropped. Patiently retrying in 30 seconds... (Reason: {e})")
            time.sleep(30)

def process_completed_alpha(index, task, task_state, alpha_id, nxt_url, run_uuid, session):
    family = task["family"]
    hypothesis = task["hypothesis"]
    formula = task["formula"]
    settings = dict(DEFAULT_SIM_SETTINGS)
    if "settings" in task and task["settings"]:
        settings.update(task["settings"])

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
        task_state["status"] = status
        task_state["progress"] = 100
        task_state["sharpe"] = sharpe
        task_state["fitness"] = fitness
        task_state["turnover"] = turnover

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
            
            submitted_ok = False
            
            if submit_r.status_code == 404:
                try:
                    alpha_url = f"{WQ_ALPHAS_URL}/{alpha_id}"
                    alpha_r = robust_request(session, "GET", alpha_url, index=index, timeout=15).json()
                    current_status = alpha_r.get("status")
                    if current_status == "SUBMITTED":
                        log_message("SUBMITTED", f"Alpha #{index+1} already submitted (verified).")
                        save_submitted_alpha(row_id, alpha_id, self_corr_pass=True)
                        submitted_ok = True
                        send_whatsapp(
                            f"✅ ALPHA SUBMITTED!\n"
                            f"Alpha #{index+1}: {family}\n"
                            f"Sharpe: {sharpe:.2f} | Fitness: {fitness:.2f} | Turnover: {turnover:.1f}%\n"
                            f"ID: {alpha_id}\n"
                            f"Link: https://brain.worldquant.com/alpha/{alpha_id}"
                        )
                    else:
                        checks = alpha_r.get("is", {}).get("checks", [])
                        failed = [c for c in checks if c.get("result") == "FAIL"]
                        err_detail = "Not submitted."
                        if failed:
                            err_detail = "; ".join([f"{c['name']}={c.get('value','')}" for c in failed])
                        log_message("WARNING", f"Alpha #{index+1} was not submitted. Verified status: {current_status}. Details: {err_detail}")
                        task_state["status"] = "HARD_REJECT"
                        task_state["error_message"] = f"Submission check failed: {err_detail}"
                        send_whatsapp(
                            f"❌ ALPHA REJECTED\n"
                            f"Alpha #{index+1}: {family}\n"
                            f"Reason: {err_detail[:120]}"
                        )
                except Exception as e:
                    log_message("WARNING", f"Alpha #{index+1} already submitted (404 received, verification failed: {e}).")
                    save_submitted_alpha(row_id, alpha_id, self_corr_pass=True)
                    submitted_ok = True

            elif submit_r.status_code in (200, 201):
                log_message("SUBMITTED", f"Alpha #{index+1}: Submission checks initiated. Polling for completion...")
                
                # Step 2: Poll GET /submit until 404 (success) per API spec
                poll_limit = 40
                for poll_i in range(poll_limit):
                    time.sleep(15 + random.uniform(1, 4))
                    poll_sub = robust_request(session, "GET", sub_url, index=index, timeout=30)
                    if poll_sub.status_code == 404:
                        # 404 = checks done. Verify status!
                        try:
                            alpha_url = f"{WQ_ALPHAS_URL}/{alpha_id}"
                            alpha_r = robust_request(session, "GET", alpha_url, index=index, timeout=15).json()
                            current_status = alpha_r.get("status")
                            if current_status == "SUBMITTED":
                                log_message("SUBMITTED", f"Alpha #{index+1} FULLY SUBMITTED to production board! ID: {alpha_id}")
                                save_submitted_alpha(row_id, alpha_id, self_corr_pass=True)
                                submitted_ok = True
                                send_whatsapp(
                                    f"✅ ALPHA SUBMITTED!\n"
                                    f"Alpha #{index+1}: {family}\n"
                                    f"Sharpe: {sharpe:.2f} | Fitness: {fitness:.2f} | Turnover: {turnover:.1f}%\n"
                                    f"ID: {alpha_id}\n"
                                    f"Link: https://brain.worldquant.com/alpha/{alpha_id}"
                                )
                            else:
                                checks = alpha_r.get("is", {}).get("checks", [])
                                failed = [c for c in checks if c.get("result") == "FAIL"]
                                err_detail = "Submission failed checks on platform."
                                if failed:
                                    err_detail = "; ".join([f"{c['name']}={c.get('value','')}" for c in failed])
                                log_message("WARNING", f"Alpha #{index+1} submission REJECTED by WQ checks: {err_detail}")
                                task_state["status"] = "HARD_REJECT"
                                task_state["error_message"] = f"Submission check failed: {err_detail}"
                                submitted_ok = False
                                send_whatsapp(
                                    f"❌ ALPHA REJECTED\n"
                                    f"Alpha #{index+1}: {family}\n"
                                    f"Reason: {err_detail[:120]}"
                                )
                        except Exception as e:
                            log_message("WARNING", f"Verification request failed for alpha {alpha_id}: {e}")
                            # Fallback
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
                        task_state["status"] = "HARD_REJECT"
                        task_state["error_message"] = f"Submission check failed: {err_detail}"
                        send_whatsapp(
                            f"❌ ALPHA REJECTED\n"
                            f"Alpha #{index+1}: {family}\n"
                            f"Reason: {err_detail[:120]}"
                        )
                        break
                    elif poll_sub.status_code in (200, 201):
                        # Check body for FAIL checks even on 2xx status code
                        if poll_sub.content:
                            try:
                                res_json = poll_sub.json()
                                checks = res_json.get("is", {}).get("checks", [])
                                failed = [c for c in checks if c.get("result") == "FAIL"]
                                if failed:
                                    err_detail = "; ".join([f"{c['name']}={c.get('value','')}" for c in failed])
                                    log_message("WARNING", f"Alpha #{index+1} submission REJECTED by WQ checks: {err_detail}")
                                    task_state["status"] = "HARD_REJECT"
                                    task_state["error_message"] = f"Submission check failed: {err_detail}"
                                    send_whatsapp(
                                        f"❌ ALPHA REJECTED\n"
                                        f"Alpha #{index+1}: {family}\n"
                                        f"Reason: {err_detail[:120]}"
                                    )
                                    break
                            except Exception:
                                pass
                        log_message("INFO", f"Alpha #{index+1}: Submission checks in progress... ({poll_i+1}/{poll_limit})")
                
                if not submitted_ok and task_state["status"] != "HARD_REJECT":
                    log_message("WARNING", f"Alpha #{index+1}: Submission polling timed out after {poll_limit} attempts.")
            else:
                err_msg = submit_r.text[:200]
                log_message("WARNING", f"Alpha #{index+1} submission POST failed: {err_msg}")
        
        # Only color FULLY SUBMITTED alphas RED (not SOFT_FAIL)
        if alpha_id and status == "SUBMITTED":
            try:
                color_r = robust_request(session, "PATCH", f"{WQ_ALPHAS_URL}/{alpha_id}", index=index, json={"color": "RED"}, timeout=30)
                if color_r.status_code == 200:
                    log_message("SUBMITTED", f"Alpha #{index+1} colored RED on WQ platform.")
                else:
                    log_message("WARNING", f"Alpha #{index+1} coloring failed: {color_r.text[:100]}")
            except Exception as e:
                log_message("ERROR", f"Error coloring alpha RED: {e}")

        # Update database status if it was modified to HARD_REJECT during submission checks
        if task_state["status"] == "HARD_REJECT":
            try:
                import sqlite3
                from src.config import DB_PATH
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("UPDATE alpha_runs SET status = 'HARD_REJECT', error_message = ? WHERE id = ?", (task_state.get("error_message"), row_id))
                conn.commit()
                conn.close()
                log_message("INFO", f"Alpha #{index+1}: Updated database status to HARD_REJECT due to submission check failure.")
            except Exception as db_err:
                log_message("ERROR", f"Failed to update database status for rejected alpha: {db_err}")

    except Exception as e:
        log_message("ERROR", f"Alpha #{index+1} metric collection failed: {e}")
        task_state["status"] = "ERROR"
        task_state["error_message"] = str(e)


def simulate_task(index, task, task_state, session):
    run_uuid = str(uuid.uuid4())[:8]
    family = task["family"]
    hypothesis = task["hypothesis"]
    formula = task["formula"]
    settings = dict(DEFAULT_SIM_SETTINGS)
    if "settings" in task and task["settings"]:
        settings.update(task["settings"])

    # Check database cache to see if already simulated (disabled to test high-concurrency simulation)
    cached = None
    if cached:
        log_message("INFO", f"Alpha #{index+1}: Found cached simulation result in database. Skipping repeat API submission.")
        task_state["status"] = cached["status"]
        task_state["progress"] = 100
        task_state["sharpe"] = cached["sharpe"]
        task_state["fitness"] = cached["fitness"]
        task_state["turnover"] = cached["turnover"]
        task_state["error_message"] = cached["error_message"]
        return

    task_state["status"] = "SIMULATING"
    task_state["progress"] = 10
    log_message("INFO", f"Alpha #{index+1}: Initiating simulation for {formula}")

    # Local Syntax and Operator validation
    from src.validator import validate_fastexpr
    is_valid, err = validate_fastexpr(formula)
    if not is_valid:
        err_msg = f"Local Validation Failed: {err}"
        log_message("ERROR", f"Alpha #{index+1}: {err_msg}")
        task_state["status"] = "ERROR"
        task_state["error_message"] = err_msg
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
            # Enforce 5-second spacing between concurrent thread submissions for Gold tier
            log_message("INFO", f"Alpha #{index+1}: Enforcing 5s submission rate-limit spacing...")
            time.sleep(5)
            r = robust_request(session, "POST", WQ_SIM_URL, index=index, json=payload, timeout=30)
            
        if r.status_code == 429:
            retry_wait = 30 + random.uniform(5, 15)
            log_message("WARNING", f"Alpha #{index+1}: Rate limit exceeded (HTTP 429). Jittered retry in {retry_wait:.1f} seconds...")
            task_state["status"] = "PENDING"
            task_state["progress"] = 0
            time.sleep(retry_wait)
            return simulate_task(index, task, task_state, session)  # Recursive retry
            
        if r.status_code not in [200, 201]:
            err_msg = f"HTTP {r.status_code}: {r.text}"
            log_message("ERROR", f"Alpha #{index+1} Submission failed: {err_msg}")
            task_state["status"] = "ERROR"
            task_state["error_message"] = err_msg
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
            task_state["status"] = "ERROR"
            task_state["error_message"] = err_msg
            return

        nxt_url = r.headers['Location']
        task_state["progress"] = 35
        log_message("INFO", f"Alpha #{index+1}: Simulation queued successfully. Link: {nxt_url}")

    except Exception as e:
        log_message("ERROR", f"Alpha #{index+1} Exception: {e}")
        task_state["status"] = "ERROR"
        task_state["error_message"] = str(e)
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
            task_state["progress"] = max(35, progress)
            log_message("INFO", f"Alpha #{index+1}: WorldQuant backtesting progress... {progress}%")

            if 'message' in res and 'error' in str(res.get('message', '')).lower():
                err_msg = res['message']
                log_message("ERROR", f"Alpha #{index+1} Syntax Check Failed: {err_msg}")
                task_state["status"] = "ERROR"
                task_state["error_message"] = err_msg
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
                task_state["status"] = "ERROR"
                task_state["error_message"] = f"Polling errors exceeded limit: {e}"
                return
        time.sleep(15)

    # Simulation Complete - Retrieve metrics
    task_state["status"] = "EVALUATING"
    task_state["progress"] = 90
    process_completed_alpha(index, task, task_state, alpha_id, nxt_url, run_uuid, session)


def simulate_batch(batch_indices, batch_tasks, batch_states, session):
    if len(batch_tasks) == 1:
        simulate_task(batch_indices[0], batch_tasks[0], batch_states[0], session)
        return

    # Multi-simulation flow
    run_uuids = [str(uuid.uuid4())[:8] for _ in batch_tasks]
    
    # 1. Local Syntax and Operator validation
    valid_indices = []
    valid_tasks = []
    valid_states = []
    valid_uuids = []
    
    from src.validator import validate_fastexpr
    for idx, t, st, uid in zip(batch_indices, batch_tasks, batch_states, run_uuids):
        st["status"] = "SIMULATING"
        st["progress"] = 10
        formula = t["formula"]
        is_valid, err = validate_fastexpr(formula)
        if not is_valid:
            err_msg = f"Local Validation Failed: {err}"
            log_message("ERROR", f"Alpha #{idx+1}: {err_msg}")
            st["status"] = "ERROR"
            st["error_message"] = err_msg
            settings = dict(DEFAULT_SIM_SETTINGS)
            if "settings" in t and t["settings"]:
                settings.update(t["settings"])
            save_alpha_run({
                "run_id": uid, "family": t["family"], "hypothesis": t["hypothesis"], "formula": formula,
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
        else:
            valid_indices.append(idx)
            valid_tasks.append(t)
            valid_states.append(st)
            valid_uuids.append(uid)

    if not valid_tasks:
        return

    if len(valid_tasks) == 1:
        simulate_task(valid_indices[0], valid_tasks[0], valid_states[0], session)
        return

    # Build WQ simulation submission body (list payload)
    payload = []
    for t in valid_tasks:
        settings = dict(DEFAULT_SIM_SETTINGS)
        if "settings" in t and t["settings"]:
            settings.update(t["settings"])
        payload.append({
            "regular": t["formula"],
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
        })

    # API request
    try:
        # Acquire submission lock to ensure sequential spaced requests
        with submission_lock:
            # Enforce 5-second spacing between concurrent thread submissions for Gold tier
            log_message("INFO", f"Batch ({len(valid_tasks)} alphas): Enforcing 5s submission rate-limit spacing...")
            time.sleep(5)
            r = robust_request(session, "POST", WQ_SIM_URL, index=valid_indices[0], json=payload, timeout=30)
            
        if r.status_code == 429:
            retry_wait = 30 + random.uniform(5, 15)
            log_message("WARNING", f"Batch ({len(valid_tasks)} alphas): Rate limit exceeded (HTTP 429). Jittered retry in {retry_wait:.1f} seconds...")
            for st in valid_states:
                st["status"] = "PENDING"
                st["progress"] = 0
            time.sleep(retry_wait)
            simulate_batch(valid_indices, valid_tasks, valid_states, session)  # Recursive retry
            return
            
        if r.status_code not in [200, 201]:
            err_msg = f"HTTP {r.status_code}: {r.text}"
            log_message("ERROR", f"Batch Submission failed: {err_msg}")
            for st, uid, t in zip(valid_states, valid_uuids, valid_tasks):
                st["status"] = "ERROR"
                st["error_message"] = err_msg
                settings = dict(DEFAULT_SIM_SETTINGS)
                if "settings" in t and t["settings"]:
                    settings.update(t["settings"])
                save_alpha_run({
                    "run_id": uid, "family": t["family"], "hypothesis": t["hypothesis"], "formula": t["formula"],
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
            log_message("ERROR", f"Batch: {err_msg}")
            for st in valid_states:
                st["status"] = "ERROR"
                st["error_message"] = err_msg
            return

        parent_url = r.headers['Location']
        for st in valid_states:
            st["progress"] = 35
        log_message("INFO", f"Batch ({len(valid_tasks)} alphas) queued successfully. Parent Link: {parent_url}")

    except Exception as e:
        log_message("ERROR", f"Batch Exception: {e}")
        for st in valid_states:
            st["status"] = "ERROR"
            st["error_message"] = str(e)
        return

    # Polling Loop
    retry_count = 0
    children = []
    while True:
        try:
            poll_r = robust_request(session, "GET", parent_url, index=valid_indices[0], timeout=30)
            if poll_r.status_code == 429:
                time.sleep(15 + random.uniform(2, 6))
                continue
            if poll_r.status_code != 200:
                log_message("WARNING", f"Batch poll HTTP status: {poll_r.status_code}")
                time.sleep(10 + random.uniform(1, 4))
                continue

            res = poll_r.json()
            if 'children' in res:
                children = res['children']
                log_message("INFO", f"Batch parent simulation completed on WQ cluster. Children count: {len(children)}")
                break

            progress = int(res.get('progress', 0) * 100)
            for st in valid_states:
                st["progress"] = max(35, progress)
            log_message("INFO", f"Batch backtesting progress... {progress}%")

            if 'message' in res and 'error' in str(res.get('message', '')).lower():
                err_msg = res['message']
                log_message("ERROR", f"Batch simulation failed: {err_msg}")
                for st, uid, t in zip(valid_states, valid_uuids, valid_tasks):
                    st["status"] = "ERROR"
                    st["error_message"] = err_msg
                    settings = dict(DEFAULT_SIM_SETTINGS)
                    if "settings" in t and t["settings"]:
                        settings.update(t["settings"])
                    save_alpha_run({
                        "run_id": uid, "family": t["family"], "hypothesis": t["hypothesis"], "formula": t["formula"],
                        "region": settings.get("region", "USA"),
                        "universe": settings.get("universe", "TOP3000"),
                        "neutralization": settings.get("neutralization", "SUBINDUSTRY"),
                        "decay": settings.get("decay", 6),
                        "truncation": settings.get("truncation", 0.08),
                        "delay": settings.get("delay", 1),
                        "sharpe": None, "fitness": None, "turnover": None,
                        "checks_passed": 0, "weight_check": "FAIL", "sub_sharpe": None, "status": "HARD_REJECT",
                        "alpha_link": None, "sim_link": parent_url, "error_message": err_msg,
                        "llm_model": "gemini-1.5-flash", "parent_id": None
                    })
                return
        except Exception as e:
            log_message("ERROR", f"Batch Polling error: {e}")
            retry_count += 1
            if retry_count > 10:
                for st in valid_states:
                    st["status"] = "ERROR"
                    st["error_message"] = f"Polling errors exceeded limit: {e}"
                return
        time.sleep(15)

    if len(children) != len(valid_tasks):
        err_msg = f"API error: children count ({len(children)}) does not match submitted batch count ({len(valid_tasks)})"
        log_message("ERROR", err_msg)
        for st in valid_states:
            st["status"] = "ERROR"
            st["error_message"] = err_msg
        return

    # Process child results individually
    for idx, t, st, uid, child_id in zip(valid_indices, valid_tasks, valid_states, valid_uuids, children):
        st["status"] = "EVALUATING"
        st["progress"] = 90
        
        child_url = f"https://api.worldquantbrain.com/simulations/{child_id}"
        try:
            child_r = robust_request(session, "GET", child_url, index=idx, timeout=30)
            if child_r.status_code != 200:
                err_msg = f"Failed to get child simulation details: HTTP {child_r.status_code}"
                log_message("ERROR", f"Alpha #{idx+1}: {err_msg}")
                st["status"] = "ERROR"
                st["error_message"] = err_msg
                continue
                
            child_res = child_r.json()
            alpha_id = child_res.get("alpha")
            if not alpha_id:
                err_msg = child_res.get("message", "Child simulation failed on WQ cluster.")
                log_message("ERROR", f"Alpha #{idx+1}: {err_msg}")
                st["status"] = "ERROR"
                st["error_message"] = err_msg
                
                settings = dict(DEFAULT_SIM_SETTINGS)
                if "settings" in t and t["settings"]:
                    settings.update(t["settings"])
                save_alpha_run({
                    "run_id": uid, "family": t["family"], "hypothesis": t["hypothesis"], "formula": t["formula"],
                    "region": settings.get("region", "USA"),
                    "universe": settings.get("universe", "TOP3000"),
                    "neutralization": settings.get("neutralization", "SUBINDUSTRY"),
                    "decay": settings.get("decay", 6),
                    "truncation": settings.get("truncation", 0.08),
                    "delay": settings.get("delay", 1),
                    "sharpe": None, "fitness": None, "turnover": None,
                    "checks_passed": 0, "weight_check": "FAIL", "sub_sharpe": None, "status": "HARD_REJECT",
                    "alpha_link": None, "sim_link": child_url, "error_message": err_msg,
                    "llm_model": "gemini-1.5-flash", "parent_id": None
                })
                continue
                
            process_completed_alpha(idx, t, st, alpha_id, child_url, uid, session)
            
        except Exception as e:
            log_message("ERROR", f"Alpha #{idx+1} result retrieval failed: {e}")
            st["status"] = "ERROR"
            st["error_message"] = str(e)


def main():
    init_db()
    
    # 1. Start Flask Web Dashboard FIRST so Render health-check passes and dashboard is immediately live!
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    log_message("INFO", "Web dashboard starting up...")
    
    # Give Flask a brief moment to bind to the port
    time.sleep(1)
    
    global active_session
    # 2. Establish WQ Session in background or catch biometric/auth errors gracefully without blocking deploy
    log_message("INFO", "Logging into WorldQuant Brain...")
    try:
        active_session = WQSession()
        log_message("INFO", "Session established successfully.")
        send_whatsapp("🚀 AlphaForge ONLINE\nServer started & logged into WorldQuant Brain successfully. Simulations beginning now!")
    except Exception as e:
        log_message("WARNING", f"Initial login authentication pending or deferred: {e}")
        log_message("WARNING", "Please open the dashboard and click 'Re-auth Session' to complete login!")
        try:
            send_whatsapp(
                f"⚠️ AUTHENTICATION PENDING\n"
                f"AlphaForge started but initial login failed for {os.getenv('WQ_EMAIL', WQ_EMAIL)}: {e}\n"
                f"Please open the dashboard and click '🔑 Re-auth Session' to complete verification!"
            )
        except Exception:
            pass

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
                send_whatsapp(f"⚠️ SERVER ALERT\nKeep-alive ping FAILED! Server may be going to sleep.\nError: {str(e)[:100]}")
            time.sleep(60)

    ping_thread = threading.Thread(target=self_ping_loop, daemon=True)
    ping_thread.start()
    log_message("INFO", "[KEEPALIVE] Self-ping thread started (interval: 60s)")

    # Dynamic Queue Scheduler State
    scheduled_formulas = set()
    completed_formulas = set()
    futures = []

    concurrency_limit = int(os.getenv("MAX_CONCURRENT_SIMS", "3"))
    log_message("INFO", f"Dynamic Queue Scheduler Active (concurrency limit: {concurrency_limit} batches of 10 alphas)...")

    with ThreadPoolExecutor(max_workers=concurrency_limit) as executor:
        try:
            while True:
                if not pipeline_active:
                    pipeline_state["status"] = "PAUSED"
                    time.sleep(3)
                    continue
                
                # Poll db/simulation_queue.json for new alphas
                queue_file = DB_DIR / "simulation_queue.json"
                if queue_file.exists():
                    try:
                        with open(queue_file, "r") as f:
                            tasks = json.load(f)
                    except Exception:
                        tasks = []
                    
                    # Detect unscheduled tasks
                    new_tasks = []
                    for task in tasks:
                        formula = task["formula"]
                        if formula not in scheduled_formulas:
                            new_tasks.append(task)
                            
                    # Group them into batches
                    if new_tasks:
                        batches = []
                        current_batch = []
                        for task in new_tasks:
                            is_super = (task.get("type") == "SUPER" or "selection" in task or "combo" in task)
                            if is_super:
                                if current_batch:
                                    batches.append(current_batch)
                                    current_batch = []
                                batches.append([task])
                            else:
                                current_batch.append(task)
                                if len(current_batch) == 10:
                                    batches.append(current_batch)
                                    current_batch = []
                        if current_batch:
                            batches.append(current_batch)
                            
                        # Submit each batch
                        for batch in batches:
                            batch_indices = []
                            batch_tasks = []
                            batch_states = []
                            for task in batch:
                                formula = task["formula"]
                                scheduled_formulas.add(formula)
                                idx = len(pipeline_state["alphas"])
                                
                                # Add to shared pipeline state dynamically
                                task_state = {
                                    "formula": formula,
                                    "family": task["family"],
                                    "hypothesis": task["hypothesis"],
                                    "status": "PENDING",
                                    "progress": 0,
                                    "sharpe": None,
                                    "fitness": None,
                                    "turnover": None,
                                    "error_message": None
                                }
                                pipeline_state["alphas"].append(task_state)
                                
                                log_message("INFO", f"Dynamic Queue: Detected and queued new alpha #{idx+1}: {formula}")
                                
                                batch_indices.append(idx)
                                batch_tasks.append(task)
                                batch_states.append(task_state)
                            
                            # Submit batch to ThreadPoolExecutor
                            def make_batch_runner(b_indices, b_tasks, b_states):
                                def batch_runner():
                                    time.sleep(1.0)
                                    simulate_batch(b_indices, b_tasks, b_states, active_session)
                                return batch_runner
                            
                            futures.append(executor.submit(make_batch_runner(batch_indices, batch_tasks, batch_states)))
                
                # Check for any completed alphas to log summaries
                for idx, alpha in enumerate(pipeline_state["alphas"]):
                    formula = alpha["formula"]
                    if formula not in completed_formulas and alpha["status"] in ("SUBMITTED", "HARD_REJECT", "SOFT_FAIL", "ERROR"):
                        completed_formulas.add(formula)
                        sharpe = f"{alpha['sharpe']:.2f}" if alpha['sharpe'] is not None else "-"
                        log_message("INFO", f"Alpha #{idx+1} finished! Status: {alpha['status']} | Sharpe: {sharpe}")

                # Update pipeline status in state
                if scheduled_formulas and len(completed_formulas) == len(scheduled_formulas):
                    if pipeline_state["status"] != "COMPLETED":
                        pipeline_state["status"] = "COMPLETED"
                        # Send WhatsApp complete alert!
                        success_count = sum(1 for a in pipeline_state["alphas"] if a["status"] == "SUBMITTED")
                        fail_count = sum(1 for a in pipeline_state["alphas"] if a["status"] in ("HARD_REJECT", "SOFT_FAIL", "ERROR"))
                        send_whatsapp(
                            f"🏁 PIPELINE COMPLETED!\n"
                            f"Total processed: {len(pipeline_state['alphas'])}\n"
                            f"✅ Submitted: {success_count}\n"
                            f"❌ Rejected/Failed: {fail_count}\n"
                            f"All operations are now idle."
                        )
                else:
                    pipeline_state["status"] = "RUNNING"
                
                # Polling interval
                time.sleep(3)
                
        except KeyboardInterrupt:
            log_message("INFO", "KeyboardInterrupt detected. Shutting down pipeline gracefully...")
            
    log_message("INFO", "Pipeline shutdown complete.")

if __name__ == "__main__":
    main()

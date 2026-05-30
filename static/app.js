// DOM Elements
const logConsole = document.getElementById("log-console");
const autoscrollChk = document.getElementById("autoscroll-chk");
const clearBtn = document.getElementById("clear-btn");
const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");
const systemStatus = document.getElementById("system-status");
const statePulse = document.getElementById("state-pulse");

// Stats Elements
const statTotalRuns = document.getElementById("stat-total-runs");
const statSubmissions = document.getElementById("stat-submissions");
const statBestSharpe = document.getElementById("stat-best-sharpe");
const statBestFitness = document.getElementById("stat-best-fitness");

// Tables Elements
const familyTableBody = document.querySelector("#family-table tbody");
const vaultTableBody = document.querySelector("#vault-table tbody");

// High-Tech Terminal Chrome & Filter Elements
const copyLogsBtn = document.getElementById("copy-logs-btn");
const downloadLogsBtn = document.getElementById("download-logs-btn");
const expandConsoleBtn = document.getElementById("expand-console-btn");
const expandIcon = document.getElementById("expand-icon");
const expandText = document.getElementById("expand-text");
const terminalWrapper = document.getElementById("terminal-wrapper");
const logSearchInput = document.getElementById("log-search-input");
const searchClearBtn = document.getElementById("search-clear-btn");
const filterPills = document.querySelectorAll(".filter-pill");

// Local State
let allLogs = []; // Array of log objects: { index, timestamp, message, type }
let logCounter = 0;
let currentFilter = "all";
let searchQuery = "";
let isFullscreen = false;

// Vault Registry State
let vaultAlphas = [];
let activeVaultTab = "all";
let vaultSearchQuery = "";

let logSource = null;
let stateSource = null;
let statsInterval = null;

// HTML Escaper for Safety
function escapeHTML(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Log Categorizer
function getLogType(msg) {
    if (msg.includes("[STATUS]")) return "status";
    if (msg.includes("[AUTH]")) return "auth";
    if (msg.includes("[GENERATOR]")) return "generator";
    if (msg.includes("[SIMULATION]")) return "simulation";
    if (msg.includes("[EVALUATOR]")) return "evaluator";
    if (msg.includes("[SUBMISSION]")) return "submission";
    if (msg.includes("[SYSTEM]")) return "system";
    if (msg.toLowerCase().includes("error") || msg.toLowerCase().includes("failed")) return "error";
    if (msg.toLowerCase().includes("warning") || msg.toLowerCase().includes("warn")) return "warning";
    return "info";
}

// Check if log matches search and category filter
function matchesFilterAndSearch(log) {
    // Category match
    if (currentFilter !== "all") {
        if (currentFilter === "error") {
            if (log.type !== "error") return false;
        } else if (log.type !== currentFilter) {
            return false;
        }
    }
    
    // Search query match (supports case-insensitive regular expressions with substring fallback)
    if (searchQuery) {
        try {
            const regex = new RegExp(searchQuery, "i");
            return regex.test(log.message) || 
                   regex.test(log.timestamp) || 
                   regex.test(log.type);
        } catch (e) {
            const query = searchQuery.toLowerCase();
            return log.message.toLowerCase().includes(query) || 
                   log.timestamp.toLowerCase().includes(query) || 
                   log.type.toLowerCase().includes(query);
        }
    }
    
    return true;
}

// Apply curated high-fidelity terminal text formatting for levels and metrics
function highlightLogText(msg) {
    let html = escapeHTML(msg);
    
    // Color-code levels dynamically
    // Cyan for [INFO] or INFO
    html = html.replace(/(\[INFO\])/gi, '<span style="color: #22d3ee; font-weight: 700;">$1</span>');
    // Amber for [WARNING], [WARN], or WARNING
    html = html.replace(/(\[WARNING\]|\[WARN\]|WARNING)/gi, '<span style="color: #fbbf24; font-weight: 700;">$1</span>');
    // Emerald Green for [SUBMITTED], [SUCCESS], SUBMITTED, or SUCCESS
    html = html.replace(/(\[SUBMITTED\]|\[SUCCESS\]|SUBMITTED|SUCCESS)/gi, '<span style="color: #34d399; font-weight: 700;">$1</span>');
    // Crimson Red for [ERROR], [FAIL], ERROR, FAILURE, or FAILED
    html = html.replace(/(\[ERROR\]|\[FAIL\]|ERROR|FAILURE|FAILED|Exception)/gi, '<span style="color: #f43f5e; font-weight: 700;">$1</span>');
    
    // Highlight Alpha IDs (e.g. USXXXXXX or alpha_...)
    html = html.replace(/(US\d{7,10}|alpha_[a-f0-9]+)/gi, '<span style="color: #c084fc; font-weight: 600; background: rgba(192, 132, 252, 0.08); padding: 1px 4px; border-radius: 4px;">$1</span>');
    
    // Highlight Sharpe ratio values (e.g. Sharpe: 1.54 or Sharpe: -0.22)
    html = html.replace(/(Sharpe:\s*[-+]?\d*\.?\d+)/gi, '<span style="color: #f472b6; font-weight: 600;">$1</span>');
    
    return html;
}

// Render a single log entry into DOM
function createAndAppendLogElement(log) {
    const lineDiv = document.createElement("div");
    lineDiv.className = `log-line ${log.type}`;
    lineDiv.setAttribute("data-index", log.index);
    
    const lineNum = String(log.index).padStart(4, "0");
    
    let tagHTML = "";
    switch(log.type) {
        case "system":
            tagHTML = `<span class="log-tag tag-system">💻 SYSTEM</span>`;
            break;
        case "status":
            tagHTML = `<span class="log-tag tag-status">⚡ STATUS</span>`;
            break;
        case "auth":
            tagHTML = `<span class="log-tag tag-auth">🔑 AUTH</span>`;
            break;
        case "generator":
            tagHTML = `<span class="log-tag tag-generator">🧬 GEN</span>`;
            break;
        case "simulation":
            tagHTML = `<span class="log-tag tag-simulation">⚙️ SIM</span>`;
            break;
        case "evaluator":
            tagHTML = `<span class="log-tag tag-evaluator">📊 EVAL</span>`;
            break;
        case "submission":
            tagHTML = `<span class="log-tag tag-submission">🚀 SUBMIT</span>`;
            break;
        case "error":
            tagHTML = `<span class="log-tag tag-error">❌ ERROR</span>`;
            break;
        case "warning":
            tagHTML = `<span class="log-tag tag-warning">⚠️ WARN</span>`;
            break;
        default:
            tagHTML = `<span class="log-tag tag-info">ℹ️ INFO</span>`;
    }
    
    // Clean tag prefix from text
    let displayMsg = log.message;
    const prefixes = ["[SYSTEM]", "[STATUS]", "[AUTH]", "[GENERATOR]", "[SIMULATION]", "[EVALUATOR]", "[SUBMISSION]"];
    prefixes.forEach(p => {
        if (displayMsg.startsWith(p)) {
            displayMsg = displayMsg.replace(p, "").trim();
        }
    });

    lineDiv.innerHTML = `
        <span class="log-gutter">${lineNum}</span>
        <span class="log-time">${log.timestamp}</span>
        ${tagHTML}
        <span class="log-text">${highlightLogText(displayMsg)}</span>
    `;
    
    logConsole.appendChild(lineDiv);
    
    if (autoscrollChk.checked) {
        logConsole.scrollTop = logConsole.scrollHeight;
    }
}

// Update stats in the terminal footer
function updateTerminalStats() {
    const total = allLogs.length;
    const filtered = allLogs.filter(matchesFilterAndSearch).length;
    const errors = allLogs.filter(l => l.type === "error").length;
    
    document.getElementById("log-count-total").textContent = total;
    document.getElementById("log-count-filtered").textContent = filtered;
    document.getElementById("log-count-errors").textContent = errors;
}

// Rebuild visual logs window from memory
function rebuildLogsDisplay() {
    logConsole.innerHTML = "";
    const filteredLogs = allLogs.filter(matchesFilterAndSearch);
    filteredLogs.forEach(log => {
        createAndAppendLogElement(log);
    });
    updateTerminalStats();
}

// Append log entry and handle dynamic UI matching
function appendLog(line) {
    const msg = line.message || "";
    const type = getLogType(msg);
    logCounter++;
    
    const logObj = {
        index: logCounter,
        timestamp: line.timestamp || new Date().toLocaleTimeString(),
        message: msg,
        type: type
    };
    
    allLogs.push(logObj);
    updateTerminalStats();
    
    if (matchesFilterAndSearch(logObj)) {
        createAndAppendLogElement(logObj);
    }
}

// Fetch Metrics Summary from API
async function fetchStats() {
    try {
        const r = await fetch("/api/stats");
        if (!r.ok) return;
        const data = await r.json();

        // Update Stat Badges
        statTotalRuns.textContent = data.total_runs || 0;
        statSubmissions.textContent = data.total_submissions || 0;
        statBestSharpe.textContent = Number(data.best_sharpe || 0).toFixed(2);
        statBestFitness.textContent = Number(data.best_fitness || 0).toFixed(2);

        // Update Family Breakdown Table
        if (familyTableBody) {
            if (data.families && data.families.length > 0) {
                familyTableBody.innerHTML = "";
                data.families.forEach(item => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td style="font-weight: 500;">${item.family}</td>
                        <td>${item.total_runs}</td>
                        <td><span class="badge badge-success">${item.submitted}</span></td>
                        <td style="font-weight: 600; color: #10b981;">${item.success_rate}%</td>
                    `;
                    familyTableBody.appendChild(tr);
                });
            } else {
                familyTableBody.innerHTML = `<tr><td colspan="4" class="empty-state">No simulation statistics recorded.</td></tr>`;
            }
        }

        // Update Alpha Vault Registry
        vaultAlphas = data.vault_alphas || [];
        renderVaultTable();

    } catch (e) {
        console.error("Failed to fetch stats summary", e);
    }
}

// Render Alpha Vault Registry
function renderVaultTable() {
    if (!vaultTableBody) return;
    
    // Filter by tab and search query
    const filtered = vaultAlphas.filter(item => {
        // Tab Filter
        if (activeVaultTab !== "all") {
            if (item.status !== activeVaultTab) return false;
        }
        
        // Search query filter (search in alpha_id, family, formula, or error_message)
        if (vaultSearchQuery) {
            const q = vaultSearchQuery.toLowerCase();
            return (item.alpha_id && item.alpha_id.toLowerCase().includes(q)) ||
                   (item.family && item.family.toLowerCase().includes(q)) ||
                   (item.formula && item.formula.toLowerCase().includes(q)) ||
                   (item.error_message && item.error_message.toLowerCase().includes(q));
        }
        
        return true;
    });
    
    // Update Badge Count
    const countBadge = document.getElementById("vault-count-badge");
    if (countBadge) {
        countBadge.textContent = `${filtered.length} / ${vaultAlphas.length} Alphas`;
    }
    
    // Render
    vaultTableBody.innerHTML = "";
    if (filtered.length === 0) {
        vaultTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">No alphas matching active filters inside vault.</td>
            </tr>
        `;
        return;
    }
    
    filtered.forEach(item => {
        const tr = document.createElement("tr");
        
        // Sharpe styling
        const sharpeVal = item.sharpe !== null ? Number(item.sharpe).toFixed(2) : "0.00";
        const isSharpeSubmittable = item.sharpe >= 1.25;
        const sharpeStyle = isSharpeSubmittable ? 'color: var(--success-color); font-weight: 800; text-shadow: 0 0 8px rgba(16, 185, 129, 0.35);' : 'font-weight: 500;';
        
        // Fitness styling
        const fitnessVal = item.fitness !== null ? Number(item.fitness).toFixed(2) : "0.00";
        const isFitnessSubmittable = item.fitness >= 1.0;
        const fitnessStyle = isFitnessSubmittable ? 'color: var(--cyan-color); font-weight: 800; text-shadow: 0 0 8px rgba(6, 182, 212, 0.35);' : 'font-weight: 500;';
        
        // Turnover styling
        const turnoverVal = item.turnover !== null ? Number(item.turnover).toFixed(1) + "%" : "0.0%";
        const turnoverStyle = item.turnover <= 30.0 ? 'color: #f3f4f6; font-weight: 600;' : 'color: var(--text-muted);';
        
        // Status Badge class and text
        let statusBadgeClass = "badge-info";
        if (item.status === "SUBMITTED") statusBadgeClass = "badge-success";
        else if (item.status === "SOFT_FAIL") statusBadgeClass = "badge-warning";
        else if (item.status === "HARD_REJECT" || item.status === "ERROR") statusBadgeClass = "badge-danger-red";
        
        // Subtext for status (like errors or soft-fails)
        let statusSubtext = "";
        if (item.error_message && item.status !== "SUBMITTED") {
            statusSubtext = `<div style="font-size: 0.65rem; color: #fca5a5; max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-top: 3px;" title="${escapeHTML(item.error_message)}">${escapeHTML(item.error_message)}</div>`;
        }
        
        // Action column
        let actionHTML = "";
        if (item.status === "SUBMITTED") {
            actionHTML = `<a href="${item.alpha_link || '#'}" target="_blank" class="action-link" style="color: var(--success-color); font-weight: 700; font-size: 0.75rem; text-shadow: 0 0 6px rgba(16, 185, 129, 0.2);">Submitted ↗</a>`;
        } else if (item.status === "SOFT_FAIL" || item.status === "HARD_REJECT") {
            actionHTML = `<span style="color: #fca5a5; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;">Rejected</span>`;
        } else {
            actionHTML = `<span style="color: var(--text-muted); font-size: 0.7rem; font-style: italic;">No Action</span>`;
        }
        
        tr.innerHTML = `
            <td>
                <div style="font-family: 'Fira Code', monospace; font-weight: 700; color: #a5b4fc; font-size: 0.775rem; display: flex; align-items: center; gap: 8px;">
                    <span>${item.alpha_id}</span>
                    <button class="chrome-btn" onclick="navigator.clipboard.writeText('${escapeHTML(item.formula)}'); alert('Copied math formula to clipboard!');" title="Copy Formula" style="padding: 1px 4px; font-size: 0.65rem; display: inline-flex;">📋 Copy</button>
                </div>
                <div style="font-size: 0.675rem; color: var(--text-muted); margin-top: 3px; max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHTML(item.family)}">${escapeHTML(item.family)}</div>
            </td>
            <td>
                <span class="badge ${statusBadgeClass}" style="font-size: 0.675rem; letter-spacing: 0.3px; text-transform: uppercase;">${item.status}</span>
                ${statusSubtext}
            </td>
            <td style="${sharpeStyle}">${sharpeVal}</td>
            <td style="${fitnessStyle}">${fitnessVal}</td>
            <td style="${turnoverStyle}">${turnoverVal}</td>
            <td>${actionHTML}</td>
        `;
        
        vaultTableBody.appendChild(tr);
    });
}

// Wire Event Streams
function startEventStreams() {
    if (logSource) logSource.close();
    if (stateSource) stateSource.close();

    // Stream Console Logs
    logSource = new EventSource("/api/logs/stream");
    
    logSource.onopen = () => {
        const dot = document.getElementById("stream-status-dot");
        const text = document.getElementById("stream-status-text");
        if (dot) dot.className = "footer-status-dot active";
        if (text) {
            text.textContent = "TELEMETRY CONNECTED";
            text.style.color = "var(--success-color)";
        }
    };
    
    logSource.onerror = () => {
        const dot = document.getElementById("stream-status-dot");
        const text = document.getElementById("stream-status-text");
        if (dot) dot.className = "footer-status-dot inactive";
        if (text) {
            text.textContent = "TELEMETRY DISCONNECTED";
            text.style.color = "var(--danger-color)";
        }
    };

    logSource.onmessage = (e) => {
        try {
            const data = JSON.parse(e.data);
            appendLog(data);
        } catch (err) {
            console.error("Error parsing log line", err);
        }
    };

    // Stream Status States
    stateSource = new EventSource("/api/state/stream");
    stateSource.onmessage = (e) => {
        try {
            const data = JSON.parse(e.data);
            const status = data.status || "AGENT INACTIVE";
            systemStatus.textContent = status;
            
            if (status.includes("INACTIVE") || status.includes("STOPPED")) {
                systemStatus.className = "status-badge";
                statePulse.className = "pulse-indicator";
                startBtn.disabled = false;
                stopBtn.disabled = true;
            } else {
                systemStatus.className = "status-badge active";
                statePulse.className = "pulse-indicator active";
                startBtn.disabled = true;
                stopBtn.disabled = false;
            }
        } catch (err) {
            console.error("Error parsing state check", err);
        }
    };
}

// Controller Actions
async function startAgent() {
    appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[SYSTEM] Sending request to boot alpha orchestration pipeline..." });
    try {
        const r = await fetch("/api/agent/start", { method: "POST" });
        if (r.ok) {
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[SYSTEM] ERROR: Failed to start agent process." });
        }
    } catch (e) {
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[SYSTEM] ERROR: Network issue starting agent: ${e}` });
    }
}

async function stopAgent() {
    appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[SYSTEM] Requesting shutdown of active loops..." });
    try {
        const r = await fetch("/api/agent/stop", { method: "POST" });
        if (r.ok) {
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    } catch (e) {
        console.error("Error stopping agent", e);
    }
}

// UI Bindings
clearBtn.addEventListener("click", () => {
    allLogs = [];
    logCounter = 0;
    logConsole.innerHTML = "";
    updateTerminalStats();
    appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[SYSTEM] Console cleared by operator." });
});

startBtn.addEventListener("click", startAgent);
stopBtn.addEventListener("click", stopAgent);

// Hook up copy logs
copyLogsBtn.addEventListener("click", () => {
    const textToCopy = allLogs
        .filter(matchesFilterAndSearch)
        .map(l => `[${l.timestamp}] [${l.type.toUpperCase()}] ${l.message}`)
        .join("\n");
        
    navigator.clipboard.writeText(textToCopy).then(() => {
        const originalText = copyLogsBtn.innerHTML;
        copyLogsBtn.innerHTML = `<span class="btn-icon">✔️</span> Copied!`;
        copyLogsBtn.style.color = "var(--success-color)";
        setTimeout(() => {
            copyLogsBtn.innerHTML = originalText;
            copyLogsBtn.style.color = "";
        }, 2000);
    }).catch(err => {
        console.error("Failed to copy logs", err);
    });
});

// Hook up download logs
downloadLogsBtn.addEventListener("click", () => {
    const textToDownload = allLogs
        .filter(matchesFilterAndSearch)
        .map(l => `[${l.timestamp}] [${l.type.toUpperCase()}] ${l.message}`)
        .join("\n");
        
    const blob = new Blob([textToDownload], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `alphaforge_telemetry_${new Date().toISOString().slice(0,10)}.log`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

// Hook up expand fullscreen toggle
expandConsoleBtn.addEventListener("click", () => {
    isFullscreen = !isFullscreen;
    if (isFullscreen) {
        terminalWrapper.classList.add("fullscreen-console");
        expandIcon.textContent = "✕";
        expandText.textContent = "Collapse";
        document.body.style.overflow = "hidden";
    } else {
        terminalWrapper.classList.remove("fullscreen-console");
        expandIcon.textContent = "⛶";
        expandText.textContent = "Expand";
        document.body.style.overflow = "";
    }
});

// Hook up search filter
logSearchInput.addEventListener("input", (e) => {
    searchQuery = e.target.value;
    if (searchQuery) {
        searchClearBtn.style.display = "block";
    } else {
        searchClearBtn.style.display = "none";
    }
    rebuildLogsDisplay();
});

searchClearBtn.addEventListener("click", () => {
    logSearchInput.value = "";
    searchQuery = "";
    searchClearBtn.style.display = "none";
    rebuildLogsDisplay();
});

// Hook up category pills
filterPills.forEach(pill => {
    pill.addEventListener("click", () => {
        filterPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        currentFilter = pill.getAttribute("data-filter");
        rebuildLogsDisplay();
    });
});

// WQ Session Expiry & Status Checker
async function pollSession() {
    try {
        const r = await fetch("/api/session");
        if (!r.ok) return;
        const data = await r.json();
        
        const btn = document.getElementById("login-btn");
        const btnText = document.getElementById("login-btn-text");
        const btnIcon = document.getElementById("login-btn-icon");
        
        if (!btn) return;
        
        const authStep = document.getElementById("pipe-step-auth");
        const authIcon = document.getElementById("pipe-step-auth-icon");
        const authDesc = document.getElementById("pipe-step-auth-desc");
        const countdownBadge = document.getElementById("session-countdown-badge");
        
        if (data.expired || data.error) {
            if (btnText) btnText.textContent = "Login (Sai)";
            if (btnIcon) btnIcon.textContent = "🔑";
            btn.style.background = "linear-gradient(135deg, var(--primary-color), var(--cyan-color))";
            btn.style.boxShadow = "0 0 10px rgba(6, 182, 212, 0.25)";
            
            // Update checklist step to expired state
            if (authStep) {
                authStep.style.color = "#f87171"; // Red text
                if (authIcon) authIcon.textContent = "⚠️";
                if (authDesc) authDesc.textContent = "Authentication expired! Please click 'Re-auth Session'.";
                if (countdownBadge) countdownBadge.style.display = "none";
            }
        } else {
            const rem = data.remaining_seconds;
            const m = Math.floor(rem / 60);
            const s = rem % 60;
            const timeStr = `${m}m ${String(s).padStart(2, "0")}s`;
            
            if (btnText) btnText.textContent = `Sai Session Active (${timeStr})`;
            if (btnIcon) btnIcon.textContent = "✅";
            btn.style.background = "linear-gradient(135deg, var(--success-color), #059669)";
            btn.style.boxShadow = "0 0 12px rgba(16, 185, 129, 0.35)";
            
            // Update checklist step to active state
            if (authStep) {
                authStep.style.color = "#10b981"; // Emerald green
                if (authIcon) authIcon.textContent = "✅";
                if (authDesc) authDesc.textContent = "Authenticated. Connected to WorldQuant Brain.";
                if (countdownBadge) {
                    countdownBadge.style.display = "inline-block";
                    countdownBadge.textContent = `Session: ${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
                    countdownBadge.style.background = "rgba(16,185,129,0.1)";
                    countdownBadge.style.color = "#10b981";
                    countdownBadge.style.borderColor = "rgba(16,185,129,0.3)";
                }
            }
        }
    } catch (e) {
        console.error("Failed to poll session details", e);
        const authStep = document.getElementById("pipe-step-auth");
        const authIcon = document.getElementById("pipe-step-auth-icon");
        const authDesc = document.getElementById("pipe-step-auth-desc");
        if (authStep) {
            authStep.style.color = "#ef4444";
            if (authIcon) authIcon.textContent = "❌";
            if (authDesc) authDesc.textContent = "Connection error while verifying session.";
        }
    }
}

// Drives the step icons, session countdown timers, and active worker progress bars of the checklist
function updatePipelineChecklist(alphas) {
    const simStep = document.getElementById("pipe-step-sim");
    const simIcon = document.getElementById("pipe-step-sim-icon");
    const simDesc = document.getElementById("pipe-step-sim-desc");
    const slotsContainer = document.getElementById("slots-progress-container");
    
    const corrStep = document.getElementById("pipe-step-corr");
    const corrIcon = document.getElementById("pipe-step-corr-icon");
    const corrDesc = document.getElementById("pipe-step-corr-desc");
    
    const submitStep = document.getElementById("pipe-step-submit");
    const submitIcon = document.getElementById("pipe-step-submit-icon");
    const submitDesc = document.getElementById("pipe-step-submit-desc");
    
    if (!alphas || alphas.length === 0) {
        // Reset checklist to idle
        if (simStep) {
            simStep.style.color = "#94a3b8";
            if (simIcon) simIcon.textContent = "⚪";
            if (simDesc) simDesc.textContent = "Waiting for queue items...";
            if (slotsContainer) {
                slotsContainer.style.display = "none";
                slotsContainer.innerHTML = "";
            }
        }
        if (corrStep) {
            corrStep.style.color = "#94a3b8";
            if (corrIcon) corrIcon.textContent = "⚪";
            if (corrDesc) corrDesc.textContent = "Pending simulation results.";
        }
        if (submitStep) {
            submitStep.style.color = "#94a3b8";
            if (submitIcon) submitIcon.textContent = "⚪";
            if (submitDesc) submitDesc.textContent = "Pending correlation validation.";
        }
        return;
    }
    
    // Group states
    const completedStatuses = ["SUBMITTED", "HARD_REJECT", "SOFT_FAIL", "ERROR"];
    const activeAlphas = alphas.filter(a => !completedStatuses.includes(a.status));
    const submittedAlphas = alphas.filter(a => a.status === "SUBMITTED");
    const rejectedAlphas = alphas.filter(a => ["HARD_REJECT", "SOFT_FAIL"].includes(a.status));
    
    // 1. Batch Worker Simulation
    if (simStep) {
        if (activeAlphas.length > 0) {
            simStep.style.color = "#fbbf24"; // Amber running color
            if (simIcon) simIcon.textContent = "⏳";
            const completedCount = alphas.length - activeAlphas.length;
            if (simDesc) simDesc.textContent = `Processing backtesting batches (${completedCount}/${alphas.length} completed).`;
            
            // Build slots dynamic progress bars
            if (slotsContainer) {
                slotsContainer.style.display = "flex";
                slotsContainer.innerHTML = "";
                
                // Group active/all slot IDs present in alphas
                const slotIds = [...new Set(alphas.map(a => a.slot_id || 1))].sort();
                slotIds.forEach(slot => {
                    const slotAlphas = alphas.filter(a => (a.slot_id || 1) === slot);
                    const slotCompleted = slotAlphas.filter(a => completedStatuses.includes(a.status)).length;
                    const slotActive = slotAlphas.filter(a => !completedStatuses.includes(a.status));
                    const avgProgress = slotAlphas.reduce((sum, a) => sum + (a.progress || 0), 0) / slotAlphas.length;
                    
                    const slotDiv = document.createElement("div");
                    slotDiv.style.display = "flex";
                    slotDiv.style.flexDirection = "column";
                    slotDiv.style.gap = "4px";
                    
                    let slotStatusText = "";
                    if (slotActive.length > 0) {
                        slotStatusText = `Simulating (${slotCompleted}/${slotAlphas.length})`;
                    } else {
                        slotStatusText = `Completed (${slotCompleted}/${slotAlphas.length})`;
                    }
                    
                    slotDiv.innerHTML = `
                        <div style="display: flex; justify-content: space-between; font-size: 0.725rem; color: #e2e8f0; margin-bottom: 2px;">
                            <span style="font-weight: 600; color: #a5f3fc;">Slot ${slot}: ${slotStatusText}</span>
                            <span style="font-family: monospace; color: #3b82f6; font-weight: 700;">${Math.round(avgProgress)}%</span>
                        </div>
                        <div style="width: 100%; height: 6px; background: rgba(255, 255, 255, 0.03); border-radius: 3px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05);">
                            <div style="width: ${avgProgress}%; height: 100%; background: linear-gradient(90deg, #3b82f6, #10b981); transition: width 0.4s ease;"></div>
                        </div>
                    `;
                    slotsContainer.appendChild(slotDiv);
                });
            }
        } else {
            // All completed
            simStep.style.color = "#10b981"; // Emerald green
            if (simIcon) simIcon.textContent = "✅";
            if (simDesc) simDesc.textContent = `All ${alphas.length} alphas processed in batch workers successfully.`;
            if (slotsContainer) {
                slotsContainer.style.display = "none";
                slotsContainer.innerHTML = "";
            }
        }
    }
    
    // 2. Self-Correlation Check
    if (corrStep) {
        const corrFailed = rejectedAlphas.some(a => (a.error_message || "").toUpperCase().includes("CORRELATION"));
        if (activeAlphas.length > 0) {
            corrStep.style.color = "#fbbf24";
            if (corrIcon) corrIcon.textContent = "⏳";
            if (corrDesc) corrDesc.textContent = "Running rolling correlation checks on WQ nodes...";
        } else {
            if (corrFailed) {
                corrStep.style.color = "#fbbf24"; // Keep warning yellow/amber
                if (corrIcon) corrIcon.textContent = "⚠️";
                if (corrDesc) corrDesc.textContent = "Self-correlation check failed for some alphas (sub-portfolio duplication).";
            } else if (submittedAlphas.length > 0) {
                corrStep.style.color = "#10b981";
                if (corrIcon) corrIcon.textContent = "✅";
                if (corrDesc) corrDesc.textContent = `Passed! ${submittedAlphas.length} alphas passed self & production correlation checks.`;
            } else {
                corrStep.style.color = "#f87171";
                if (corrIcon) corrIcon.textContent = "❌";
                if (corrDesc) corrDesc.textContent = "All simulated alphas failed validation/correlation criteria.";
            }
        }
    }
    
    // 3. Platform Submission
    if (submitStep) {
        if (activeAlphas.length > 0) {
            submitStep.style.color = "#94a3b8";
            if (submitIcon) submitIcon.textContent = "⚪";
            if (submitDesc) submitDesc.textContent = "Awaiting final batch worker completion.";
        } else {
            if (submittedAlphas.length > 0) {
                submitStep.style.color = "#10b981";
                if (submitIcon) submitIcon.textContent = "✅";
                if (submitDesc) submitDesc.textContent = `Successfully submitted ${submittedAlphas.length} alphas into your WorldQuant Brain account!`;
            } else {
                submitStep.style.color = "#f87171";
                if (submitIcon) submitIcon.textContent = "❌";
                if (submitDesc) submitDesc.textContent = "No alphas pushed. All submissions failed/rejected.";
            }
        }
    }
}

// Fetch and render the active backtesting simulation queue
async function pollQueueStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) return;
        const data = await res.json();
        
        const listContainer = document.getElementById("alpha-list");
        const progressBadge = document.getElementById("queue-progress-badge");
        
        if (!listContainer) return;
        
        const alphas = data.alphas || [];
        updatePipelineChecklist(alphas);
        
        if (alphas.length === 0) {
            listContainer.innerHTML = `<div class="empty-state">No alphas currently simulating in queue.</div>`;
            if (progressBadge) progressBadge.textContent = "0 / 0 Completed";
            return;
        }
        
        let completedCount = 0;
        listContainer.innerHTML = "";
        
        alphas.forEach((alpha, index) => {
            if (["SUBMITTED", "HARD_REJECT", "SOFT_FAIL", "ERROR"].includes(alpha.status)) {
                completedCount++;
            }
            
            const card = document.createElement("div");
            let stateClass = "";
            if (alpha.status === "SIMULATING") stateClass = "simulating";
            else if (alpha.status === "SUBMITTED") stateClass = "submitted";
            else if (alpha.status === "EVALUATING") stateClass = "evaluating";
            else if (["HARD_REJECT", "SOFT_FAIL", "ERROR"].includes(alpha.status)) stateClass = "failed";
            card.className = `alpha-card ${stateClass}`;
            
            const sharpeVal = alpha.sharpe !== null ? Number(alpha.sharpe).toFixed(2) : "-";
            const fitnessVal = alpha.fitness !== null ? Number(alpha.fitness).toFixed(2) : "-";
            const turnoverVal = alpha.turnover !== null ? Number(alpha.turnover).toFixed(1) + "%" : "-";
            
            let statusBadgeClass = "badge-info";
            if (alpha.status === "SUBMITTED") statusBadgeClass = "badge-success";
            else if (alpha.status === "SIMULATING") statusBadgeClass = "badge-warning";
            else if (alpha.status === "EVALUATING") statusBadgeClass = "badge-primary";
            else if (["HARD_REJECT", "SOFT_FAIL", "ERROR"].includes(alpha.status)) statusBadgeClass = "badge-danger";
            
            const isError = !!alpha.error_message;
            const rawDescText = alpha.error_message || alpha.hypothesis || "";
            
            let slotBadgeHTML = "";
            if (alpha.slot_id) {
                let slotBadgeClass = `badge-slot-${alpha.slot_id}`;
                slotBadgeHTML = `<span class="badge ${slotBadgeClass}">Slot ${alpha.slot_id}</span>`;
            }
            
            card.innerHTML = `
                <div class="alpha-card-header">
                    <span class="alpha-card-family" title="${escapeHTML(alpha.family)}">#${index + 1}: ${escapeHTML(alpha.family)}</span>
                    <div style="display: flex; gap: 6px; align-items: center;">
                        <span class="badge ${statusBadgeClass}">${alpha.status}</span>
                        ${slotBadgeHTML}
                        <button class="delete-alpha-btn" data-formula="${escapeHTML(alpha.formula)}" style="background: none; border: none; color: #f87171; cursor: pointer; font-size: 0.85rem; padding: 0 4px; display: inline-flex; align-items: center; outline: none; transition: transform 0.2s ease;" title="Delete this alpha from queue">❌</button>
                    </div>
                </div>
                <div class="alpha-card-formula" title="${escapeHTML(alpha.formula)}">${escapeHTML(alpha.formula)}</div>
                <div class="alpha-card-meta">
                    <span style="font-size: 0.7rem; min-width: 0; flex-grow: 1; margin-right: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: block;${isError ? ' color: var(--danger-color); font-weight: 500;' : ''}" title="${escapeHTML(rawDescText)}">
                        ${escapeHTML(rawDescText)}
                    </span>
                    <div class="alpha-card-metrics" style="flex-shrink: 0;">
                        <span>S: <strong style="color: var(--primary-color)">${sharpeVal}</strong></span>
                        <span>F: <strong style="color: var(--success-color)">${fitnessVal}</strong></span>
                        <span>T: <strong>${turnoverVal}</strong></span>
                    </div>
                </div>
                <div class="alpha-card-progress-wrapper">
                    <div class="alpha-card-progress" style="width: ${alpha.progress || 0}%"></div>
                </div>
            `;
            
            listContainer.appendChild(card);
        });
        
        if (progressBadge) {
            progressBadge.textContent = `${completedCount} / ${alphas.length} Completed`;
        }
        
    } catch (e) {
        console.error("Failed to poll queue status", e);
    }
}

// Re-authentication Interactive Flow
const reauthBtn = document.getElementById("login-btn");
if (reauthBtn) {
    const reauthModal = document.getElementById("reauth-modal");
    const reauthModalIcon = document.getElementById("reauth-modal-icon");
    const reauthModalTitle = document.getElementById("reauth-modal-title");
    const reauthModalText = document.getElementById("reauth-modal-text");
    const reauthModalLink = document.getElementById("reauth-modal-link");
    const reauthModalLoader = document.getElementById("reauth-modal-loader");
    const reauthModalClose = document.getElementById("reauth-modal-close");

    let reauthPollInterval = null;

    async function triggerReauth() {
        const btnText = document.getElementById("login-btn-text");
        const btnIcon = document.getElementById("login-btn-icon");

        appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[AUTH] Initiating interactive re-authentication request..." });
        reauthBtn.disabled = true;
        if (btnText) btnText.textContent = "Logging in...";
        if (btnIcon) btnIcon.textContent = "🔑";
        
        try {
            const r = await fetch("/api/reauthenticate", { method: "POST" });
            if (!r.ok) {
                throw new Error(`HTTP ${r.status}`);
            }
            const data = await r.json();
            
            if (data.status === "SUCCESS") {
                appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[AUTH] Session verified! Authenticated successfully using saved state." });
                if (btnText) btnText.textContent = "Session Live";
                if (btnIcon) btnIcon.textContent = "✅";
                reauthBtn.style.background = "linear-gradient(135deg, var(--success-color), #059669)";
                setTimeout(() => {
                    reauthBtn.disabled = false;
                    pollSession(); // Restore remaining seconds countdown
                }, 3000);
                pollSession(); // Immediately update timer badge!
            } else if (data.status === "POLLING") {
                // Persona challenge required!
                const biometricUrl = data.url;
                appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[AUTH] Biometric verification challenge generated. Redirecting to: ${biometricUrl}` });
                
                // 1. Set modal attributes
                reauthModalLink.href = biometricUrl;
                reauthModalIcon.textContent = "🔐";
                reauthModalIcon.style.animation = "pulse 2s infinite";
                reauthModalTitle.textContent = "Biometric Verification Required";
                reauthModalText.innerHTML = `WorldQuant requires Persona biometric verification to securely authenticate your session.<br><strong style="color: #fca5a5; font-weight: bold;">Please complete verification in the new tab.</strong>`;
                reauthModalLoader.style.display = "flex";
                reauthModalLink.style.display = "inline-block";
                
                // 2. Open Persona in a new tab immediately
                window.open(biometricUrl, "_blank");
                
                // 3. Open Modal
                reauthModal.style.display = "flex";
                
                // 4. Start polling for confirmation
                if (reauthPollInterval) clearInterval(reauthPollInterval);
                reauthPollInterval = setInterval(async () => {
                    try {
                        const statusRes = await fetch("/api/reauth-status");
                        if (!statusRes.ok) return;
                        const statusData = await statusRes.json();
                        
                        if (statusData.status === "SUCCESS") {
                            clearInterval(reauthPollInterval);
                            appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[AUTH] Persona biometric verification confirmed! Session successfully updated." });
                            
                            // Update Modal to Success State
                            reauthModalIcon.textContent = "✅";
                            reauthModalIcon.style.animation = "";
                            reauthModalTitle.textContent = "Verification Complete!";
                            reauthModalText.textContent = "Your WorldQuant Brain session is now fully authenticated and active.";
                            reauthModalLoader.style.display = "none";
                            reauthModalLink.style.display = "none";
                            
                            reauthBtn.disabled = false;
                            if (btnText) btnText.textContent = "Session Live";
                            if (btnIcon) btnIcon.textContent = "✅";
                            reauthBtn.style.background = "linear-gradient(135deg, var(--success-color), #059669)";
                            
                            // Close modal after 2.5 seconds
                            setTimeout(() => {
                                reauthModal.style.display = "none";
                                pollSession();
                            }, 2500);
                        } else if (statusData.status === "ERROR") {
                            clearInterval(reauthPollInterval);
                            appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[AUTH] Re-authentication failed: ${statusData.error}` });
                            
                            // Update Modal to Error State
                            reauthModalIcon.textContent = "❌";
                            reauthModalIcon.style.animation = "";
                            reauthModalTitle.textContent = "Verification Failed";
                            reauthModalText.textContent = statusData.error || "A problem occurred during biometric verification.";
                            reauthModalLoader.style.display = "none";
                            reauthModalLink.style.display = "none";
                            
                            reauthBtn.disabled = false;
                            if (btnText) btnText.textContent = "Login Failed";
                            if (btnIcon) btnIcon.textContent = "❌";
                            reauthBtn.style.background = "linear-gradient(135deg, #ef4444, #dc2626)";
                            setTimeout(() => {
                                pollSession();
                            }, 3000);
                        }
                    } catch (pollErr) {
                        console.error("Error polling reauth status", pollErr);
                    }
                }, 3000);
            } else {
                throw new Error(data.error || "Unknown authentication state");
            }
        } catch (err) {
            appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[AUTH] Authentication initiation failed: ${err.message}` });
            reauthBtn.disabled = false;
            if (btnText) btnText.textContent = "Login Failed";
            if (btnIcon) btnIcon.textContent = "❌";
            alert(`Authentication Initiation Failed:\n${err.message}`);
            setTimeout(() => {
                pollSession();
            }, 3000);
        }
    }

    // Close Modal Bindings
    reauthModalClose.addEventListener("click", () => {
        if (reauthPollInterval) clearInterval(reauthPollInterval);
        reauthModal.style.display = "none";
        reauthBtn.disabled = false;
        pollSession();
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[AUTH] Interactive re-authentication canceled by operator." });
    });

    // Wire up button click
    reauthBtn.addEventListener("click", triggerReauth);
}

// Dynamic Alpha Injector Integration
const injFormula = document.getElementById("inj-formula");
const injFamily = document.getElementById("inj-family");
const injHypothesis = document.getElementById("inj-hypothesis");
const injSubmitBtn = document.getElementById("inj-submit-btn");

async function injectAlpha() {
    const formulaVal = injFormula.value.trim();
    const familyVal = injFamily.value.trim() || "Dynamic Entry";
    const hypothesisVal = injHypothesis.value.trim() || "Manual formula injection";
    
    if (!formulaVal) {
        alert("Please enter a mathematical formula before injecting!");
        return;
    }
    
    injSubmitBtn.disabled = true;
    injSubmitBtn.innerHTML = `⚙️ Injecting...`;
    appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[SYSTEM] Injecting manual alpha formula into backtesting queue: ${formulaVal}` });
    
    try {
        const res = await fetch("/api/queue-alpha-direct", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                formula: formulaVal,
                family: familyVal,
                hypothesis: hypothesisVal
            })
        });
        
        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.error || `HTTP ${res.status}`);
        }
        
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[SYSTEM] Alpha successfully injected into dynamic backtesting queue!" });
        injFormula.value = "";
        injFamily.value = "";
        injHypothesis.value = "";
        
        // Refresh queue status immediately
        pollQueueStatus();
        
        // Success micro-animation
        const originalBg = injSubmitBtn.style.background;
        injSubmitBtn.style.background = "linear-gradient(135deg, #10b981, #059669)";
        injSubmitBtn.innerHTML = `✅ Injected Successfully!`;
        setTimeout(() => {
            injSubmitBtn.disabled = false;
            injSubmitBtn.innerHTML = `🚀 Inject into Backtest Queue`;
            injSubmitBtn.style.background = originalBg;
        }, 2000);
        
    } catch (e) {
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[SYSTEM] ERROR: Injection failed: ${e.message}` });
        injSubmitBtn.disabled = false;
        injSubmitBtn.innerHTML = `🚀 Inject into Backtest Queue`;
        alert(`Failed to inject alpha:\n${e.message}`);
    }
}

if (injSubmitBtn) {
    injSubmitBtn.addEventListener("click", injectAlpha);
}

// Queue Clean Integration
const cleanQueueBtn = document.getElementById("clean-queue-btn");
cleanQueueBtn.addEventListener("click", async () => {
    cleanQueueBtn.disabled = true;
    cleanQueueBtn.innerHTML = `🧹 Cleaning...`;
    appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[SYSTEM] Cleaning dynamic queue (removing errored & failed alphas)..." });
    
    try {
        const res = await fetch("/api/clean-queue", { method: "POST" });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[SYSTEM] Dynamic queue cleaned successfully." });
        pollQueueStatus();
    } catch (e) {
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[SYSTEM] ERROR: Failed to clean queue: ${e.message}` });
        alert(`Failed to clean queue: ${e.message}`);
    } finally {
        cleanQueueBtn.disabled = false;
        cleanQueueBtn.innerHTML = `🧹 Clean`;
    }
});

// Queue Purge Integration
const purgeQueueBtn = document.getElementById("purge-queue-btn");
purgeQueueBtn.addEventListener("click", async () => {
    if (!confirm("⚠️ WARNING!\nAre you sure you want to completely PURGE all pending and simulated alphas from the queue?\nThis action cannot be undone.")) {
        return;
    }
    
    purgeQueueBtn.disabled = true;
    purgeQueueBtn.innerHTML = `🗑️ Purging...`;
    appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[SYSTEM] Initiating complete purge of dynamic backtesting queue..." });
    
    try {
        const res = await fetch("/api/clear-queue", { method: "POST" });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[SYSTEM] Dynamic queue fully purged." });
        
        // Hard-clear local memory lists
        const listContainer = document.getElementById("alpha-list");
        if (listContainer) {
            listContainer.innerHTML = `<div class="empty-state">No alphas currently simulating in queue.</div>`;
        }
        const progressBadge = document.getElementById("queue-progress-badge");
        if (progressBadge) progressBadge.textContent = "0 / 0 Completed";
        
        // Full refresh
        window.location.reload();
    } catch (e) {
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[SYSTEM] ERROR: Failed to purge queue: ${e.message}` });
        alert(`Failed to purge queue: ${e.message}`);
        purgeQueueBtn.disabled = false;
        purgeQueueBtn.innerHTML = `🗑️ Purge All`;
    }
});

// Queue Clear Top 50 Integration
const purgeTop50Btn = document.getElementById("purge-top50-btn");
if (purgeTop50Btn) {
    purgeTop50Btn.addEventListener("click", async () => {
        if (!confirm("⚠️ WARNING!\nAre you sure you want to clear the first 50 alphas from the dynamic simulation queue?\nThis action cannot be undone.")) {
            return;
        }
        
        purgeTop50Btn.disabled = true;
        purgeTop50Btn.innerHTML = `🧹 Clearing...`;
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[SYSTEM] Initiating purge of top 50 pending dynamic alphas from the queue..." });
        
        try {
            const res = await fetch("/api/clear-top-50", { method: "POST" });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            
            appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[SYSTEM] Successfully cleared top ${data.cleared || 0} alphas from backtesting queue.` });
            
            // Reload dashboard to refresh active list and state
            window.location.reload();
        } catch (e) {
            appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[SYSTEM] ERROR: Failed to clear top 50: ${e.message}` });
            alert(`Failed to clear top 50 queue: ${e.message}`);
            purgeTop50Btn.disabled = false;
            purgeTop50Btn.innerHTML = `🧹 Clear Top 50`;
        }
    });
}

// Vault Purge & Reset Integration
const purgeVaultBtn = document.getElementById("purge-vault-btn");
if (purgeVaultBtn) {
    purgeVaultBtn.addEventListener("click", async () => {
        if (!confirm("🚨 WARNING! HIGH-RISK OPERATION 🚨\nAre you sure you want to completely PURGE the Alpha Vault database and delete all local generated files?\nThis will wipe out all past backtesting progress and cannot be undone.")) {
            return;
        }
        if (!confirm("CONFIRMATION REQUIRED:\nDo you really want to clear the quantitative registry tables completely?")) {
            return;
        }
        
        purgeVaultBtn.disabled = true;
        purgeVaultBtn.innerHTML = `🧹 Purging...`;
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[SYSTEM] Initiating full database purge & vault registry optimization..." });
        
        try {
            const res = await fetch("/api/purge-vault", { method: "POST" });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            
            appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[SYSTEM] Alpha Vault Registry successfully purged and optimized via SQLite VACUUM." });
            alert("Alpha Vault and local files successfully purged!");
            
            window.location.reload();
        } catch (e) {
            appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[SYSTEM] ERROR: Failed to purge vault: ${e.message}` });
            alert(`Failed to purge vault: ${e.message}`);
            purgeVaultBtn.disabled = false;
            purgeVaultBtn.innerHTML = `🧹 Purge Vault`;
        }
    });
}

// Event delegation for deleting individual alphas from simulation queue
const alphaListContainer = document.getElementById("alpha-list");
if (alphaListContainer) {
    alphaListContainer.addEventListener("click", async (event) => {
        // Find if target or any parent is .delete-alpha-btn
        const deleteBtn = event.target.closest(".delete-alpha-btn");
        if (!deleteBtn) return;
        
        const formula = deleteBtn.getAttribute("data-formula");
        if (!formula) return;
        
        if (!confirm(`⚠️ Confirm Deletion\nAre you sure you want to delete this alpha from the dynamic backtesting queue?\nFormula: ${formula.slice(0, 80)}...`)) {
            return;
        }
        
        // Visual feedback: fade card
        const card = deleteBtn.closest(".alpha-card");
        if (card) {
            card.style.opacity = "0.4";
            card.style.pointerEvents = "none";
        }
        
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[SYSTEM] Requesting deletion of specific alpha: ${formula.slice(0, 50)}...` });
        
        try {
            const res = await fetch("/api/delete-alpha", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ formula: formula })
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            
            appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[SYSTEM] Specific alpha successfully deleted from backtesting queue.` });
            
            // Instantly poll queue to redraw UI seamlessly without full reload!
            if (typeof pollQueueStatus === "function") {
                await pollQueueStatus();
            } else {
                window.location.reload();
            }
        } catch (e) {
            appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[SYSTEM] ERROR: Failed to delete alpha: ${e.message}` });
            alert(`Failed to delete alpha: ${e.message}`);
            if (card) {
                card.style.opacity = "";
                card.style.pointerEvents = "";
            }
        }
    });
}

// CSV Portfolio Exporter
const exportVaultBtn = document.getElementById("export-vault-btn");
exportVaultBtn.addEventListener("click", () => {
    if (!vaultAlphas || vaultAlphas.length === 0) {
        alert("No simulated alphas in vault registry to export!");
        return;
    }
    
    appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[SYSTEM] Exporting Alpha Vault portfolio as CSV..." });
    
    // Compile CSV headers & data rows
    const headers = ["Alpha ID", "Family", "Status", "Sharpe", "Fitness", "Turnover", "Formula", "Error Message", "Link"];
    const rows = vaultAlphas.map(item => [
        item.alpha_id || "",
        `"${(item.family || "Unknown").replace(/"/g, '""')}"`,
        item.status || "",
        item.sharpe !== null ? item.sharpe.toFixed(4) : "0.0",
        item.fitness !== null ? item.fitness.toFixed(4) : "0.0",
        item.turnover !== null ? (item.turnover / 100).toFixed(4) : "0.0",
        `"${(item.formula || "").replace(/"/g, '""')}"`,
        `"${(item.error_message || "").replace(/"/g, '""')}"`,
        item.alpha_link || "#"
    ]);
    
    const csvContent = [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
    
    // Trigger download
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `alphaforge_vault_export_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

// WQ Review Inbox System Client-Side Integration
async function pollInboxAlphas() {
    try {
        const res = await fetch("/api/inbox-alphas");
        if (!res.ok) return;
        const data = await res.json();
        
        const listContainer = document.getElementById("inbox-list");
        const countBadge = document.getElementById("inbox-count");
        
        if (!listContainer) return;
        
        if (countBadge) {
            countBadge.textContent = `${data.length} Pending`;
            countBadge.style.display = data.length > 0 ? "inline-block" : "none";
        }
        
        if (data.length === 0) {
            listContainer.innerHTML = `<div style="text-align: center; color: var(--text-muted); font-size: 0.7rem; padding: 15px 0;">No pending API formulas to review.</div>`;
            return;
        }
        
        listContainer.innerHTML = "";
        data.forEach((alpha, idx) => {
            const card = document.createElement("div");
            card.className = "alpha-card";
            
            // Standardized alpha-card styling structure (exact match to queue)
            card.innerHTML = `
                <div class="alpha-card-header">
                    <span class="alpha-card-family" title="${escapeHTML(alpha.family || 'API Push')}">#${idx + 1}: ${escapeHTML(alpha.family || 'API Push')}</span>
                    <button class="chrome-btn inbox-push-btn" style="padding: 3px 8px; font-size: 0.65rem; font-weight: 700; background: rgba(244, 63, 94, 0.15); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 4px; cursor: pointer; outline: none; transition: all 0.2s ease;">Push 🚀</button>
                </div>
                <div class="alpha-card-formula" title="${escapeHTML(alpha.formula)}">${escapeHTML(alpha.formula)}</div>
                <div class="alpha-card-meta">
                    <span style="font-size: 0.65rem; color: var(--text-muted); display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; width: 100%;" title="${escapeHTML(alpha.hypothesis || '')}">
                        ${escapeHTML(alpha.hypothesis || 'No description provided.')}
                    </span>
                </div>
            `;
            
            // Wire up premium hover states and click events for the button
            const pushBtn = card.querySelector(".inbox-push-btn");
            pushBtn.addEventListener("mouseenter", () => {
                pushBtn.style.background = "#f43f5e";
                pushBtn.style.color = "white";
                pushBtn.style.boxShadow = "0 0 8px rgba(244, 63, 94, 0.4)";
            });
            pushBtn.addEventListener("mouseleave", () => {
                pushBtn.style.background = "rgba(244, 63, 94, 0.15)";
                pushBtn.style.color = "#f43f5e";
                pushBtn.style.boxShadow = "none";
            });
            pushBtn.addEventListener("click", async () => {
                pushBtn.disabled = true;
                pushBtn.textContent = "⚙️...";
                await pushInboxAlpha(alpha.formula);
            });
            
            listContainer.appendChild(card);
        });
    } catch (e) {
        console.error("Failed to poll inbox status", e);
    }
}

async function pushInboxAlpha(formula) {
    appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[INJECTOR] Manually pushing reviewed alpha into backtest queue: ${formula}` });
    try {
        const res = await fetch("/api/inject-inbox", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ formulas: [formula] })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[INJECTOR] Alpha successfully pushed to dynamic backtest queue!" });
        pollInboxAlphas();
        pollQueueStatus();
    } catch (e) {
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[INJECTOR] ERROR: Failed to push alpha: ${e.message}` });
        alert(`Failed to push alpha:\n${e.message}`);
    }
}

async function pushAllInbox() {
    const count = parseInt(document.getElementById("inbox-count")?.textContent || "0");
    if (count === 0) return;
    
    appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[INJECTOR] Push All triggered: Injecting all ${count} pending review alphas into active backtesting queue...` });
    try {
        const res = await fetch("/api/inject-inbox", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ all: true })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[INJECTOR] Successfully pushed all ${count} alphas to dynamic backtesting queue!` });
        pollInboxAlphas();
        pollQueueStatus();
    } catch (e) {
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: `[INJECTOR] ERROR: Batch push failed: ${e.message}` });
        alert(`Batch push failed:\n${e.message}`);
    }
}

async function clearInbox() {
    const count = parseInt(document.getElementById("inbox-count")?.textContent || "0");
    if (count === 0) return;
    
    if (!confirm(`Are you sure you want to discard and clear all ${count} pending API formulas?`)) {
        return;
    }
    
    try {
        const res = await fetch("/api/clear-inbox", { method: "POST" });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[INJECTOR] Discarded and cleared all pending review alphas from inbox." });
        pollInboxAlphas();
    } catch (e) {
        console.error("Failed to clear inbox", e);
    }
}

// ==========================================
// SUBMISSION PLATFORM CODE
// ==========================================
let submissionQueue = [];
let subActiveTab = "green"; // green or yellow
let submissionLogLines = [];

function appendSubmissionLog(message) {
    const consoleElem = document.getElementById("submission-log-console");
    if (!consoleElem) return;
    
    // If it's the initial placeholder, clear it
    if (submissionLogLines.length === 0) {
        consoleElem.innerHTML = "";
    }
    
    const timestamp = new Date().toLocaleTimeString();
    const formattedLine = `[${timestamp}] ${message}`;
    submissionLogLines.push(formattedLine);
    
    const lineDiv = document.createElement("div");
    lineDiv.style.marginBottom = "4px";
    lineDiv.style.lineHeight = "1.4";
    
    // Set colors based on keywords
    if (message.includes("[SUCCESS]")) {
        lineDiv.style.color = "#10b981"; // green
    } else if (message.includes("[FAILED]") || message.includes("rejected")) {
        lineDiv.style.color = "#ef4444"; // red
    } else if (message.includes("permanently rejected") || message.includes("YELLOW")) {
        lineDiv.style.color = "#fbbf24"; // yellow
    } else {
        lineDiv.style.color = "#a5f3fc"; // cyan
    }
    
    lineDiv.textContent = formattedLine;
    consoleElem.appendChild(lineDiv);
    
    // Auto scroll to bottom
    consoleElem.scrollTop = consoleElem.scrollHeight;
}

// 1. Fetch platform stats
async function fetchPlatformStats() {
    try {
        const res = await fetch("/api/platform-stats");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        
        document.getElementById("sub-queue-count").textContent = data.queue_count || 0;
        document.getElementById("sub-green-count").textContent = data.green_count || 0;
        document.getElementById("sub-yellow-count").textContent = data.yellow_count || 0;
        document.getElementById("sub-total-count").textContent = data.total_count || 0;
        document.getElementById("queue-count-badge").textContent = `${data.queue_count || 0} Queued`;
    } catch (e) {
        console.error("Failed to fetch platform stats", e);
    }
}

// 2. Load submission queue
async function loadSubmissionQueue() {
    try {
        const res = await fetch("/api/submission-queue");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        submissionQueue = await res.json();
        renderSubmissionQueueTable();
    } catch (e) {
        console.error("Failed to load submission queue", e);
    }
}

// 3. Render submission queue
function renderSubmissionQueueTable() {
    const tbody = document.getElementById("sub-queue-body");
    if (!tbody) return;
    
    const searchVal = document.getElementById("queue-search-input")?.value?.toLowerCase() || "";
    
    // Filter queue
    let filtered = submissionQueue.filter(item => {
        if (!searchVal) return true;
        return item.alpha_id.toLowerCase().includes(searchVal) ||
               item.formula.toLowerCase().includes(searchVal) ||
               item.status.toLowerCase().includes(searchVal);
    });
    
    // Render list
    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No matching submittable alphas in queue.</td></tr>`;
        return;
    }
    
    tbody.innerHTML = "";
    filtered.forEach(item => {
        const tr = document.createElement("tr");
        
        // Status Badge Style
        let badgeClass = "badge-neutral";
        let rowStyle = "";
        
        if (item.status === "GREEN") {
            badgeClass = "badge-success";
            rowStyle = "background-color: rgba(16, 185, 129, 0.05);";
        } else if (item.status === "YELLOW") {
            badgeClass = "badge-warning";
            rowStyle = "background-color: rgba(245, 158, 11, 0.05);";
        } else if (item.status === "RED") {
            badgeClass = "badge-danger";
            rowStyle = "background-color: rgba(239, 68, 68, 0.05);";
        }
        
        tr.style.cssText = rowStyle;
        
        tr.innerHTML = `
            <td style="text-align: center;">
                <input type="checkbox" class="queue-row-chk" data-id="${item.alpha_id}" style="cursor: pointer;">
            </td>
            <td>
                <div style="font-weight: 700; color: white; font-family: monospace;">${item.alpha_id}</div>
                <div style="font-size: 0.7rem; color: var(--text-muted, #94a3b8); font-family: monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 320px;" title="${escapeHTML(item.formula)}">${escapeHTML(item.formula)}</div>
            </td>
            <td>${item.sharpe ? item.sharpe.toFixed(2) : "0.00"}</td>
            <td>${item.fitness ? item.fitness.toFixed(2) : "0.00"}</td>
            <td>${item.turnover ? item.turnover.toFixed(1) : "0.0"}%</td>
            <td>
                <span class="badge ${badgeClass}">${item.status}</span>
            </td>
            <td>
                <button class="chrome-btn single-submit-btn" data-id="${item.alpha_id}" style="padding: 4px 8px; font-size: 0.725rem; font-weight: 700; background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.3); border-radius: 6px; cursor: pointer; outline: none; color: #34d399;">Submit</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
    
    // Wire up single submit buttons
    tbody.querySelectorAll(".single-submit-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const alphaId = btn.getAttribute("data-id");
            triggerSubmission([alphaId]);
        });
    });
}

// 4. Trigger Submission
async function triggerSubmission(alphaIds) {
    if (alphaIds.length === 0) {
        alert("Please select at least one alpha to submit.");
        return;
    }
    
    appendSubmissionLog(`Initiating submission process for ${alphaIds.length} alphas...`);
    
    try {
        const res = await fetch("/api/submit-alphas", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ alpha_ids: alphaIds })
        });
        
        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.message || `HTTP ${res.status}`);
        }
        
        appendSubmissionLog("[SYSTEM] Sequencer active. Bulk execution initialized.");
        pollSubmissionStatus();
    } catch (e) {
        appendSubmissionLog(`[ERROR] Submission request failed: ${e.message}`);
        alert(`Failed to start submission: ${e.message}`);
    }
}

// 5. Poll Submission Sequencer Status
let subPollInterval = null;
function pollSubmissionStatus() {
    if (subPollInterval) return;
    
    subPollInterval = setInterval(async () => {
        try {
            const res = await fetch("/api/submission-status");
            if (!res.ok) throw new Error();
            const data = await res.json();
            
            if (data.status === "RUNNING") {
                appendSubmissionLog(`[SEQUENCER] Progress: ${data.current_index}/${data.total} | Current ID: ${data.current_alpha_id} | Success: ${data.success_count} | Failed: ${data.fail_count}`);
            } else if (data.status === "SUCCESS") {
                appendSubmissionLog(`[SUCCESS] Sequencer finished. ${data.success_count} successful, ${data.fail_count} failed.`);
                clearInterval(subPollInterval);
                subPollInterval = null;
                // Reload tables
                loadSubmissionQueue();
                fetchPlatformStats();
                loadSubmissionRegistry();
            } else if (data.status === "ERROR") {
                appendSubmissionLog(`[ERROR] Sequencer failure: ${data.message}`);
                clearInterval(subPollInterval);
                subPollInterval = null;
                loadSubmissionQueue();
                fetchPlatformStats();
                loadSubmissionRegistry();
            }
        } catch (e) {
            console.error("Error polling submission status", e);
        }
    }, 2000);
}

// 6. Start Search (Platform Sweep)
async function startSearch() {
    const searchBtn = document.getElementById("start-search-btn");
    const progressText = document.getElementById("search-progress-text");
    
    if (searchBtn) searchBtn.disabled = true;
    if (progressText) {
        progressText.style.display = "block";
        progressText.textContent = "Scanning platform for qualifying alphas...";
    }
    
    appendSubmissionLog("Initiating scan for qualifying alphas (Sharpe >= 1.5, Fitness >= 1.0)...");
    
    try {
        const res = await fetch("/api/sweep-platform-alphas", { method: "POST" });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        pollSweepStatus();
    } catch (e) {
        appendSubmissionLog(`[ERROR] Sweep trigger failed: ${e.message}`);
        if (searchBtn) searchBtn.disabled = false;
        if (progressText) progressText.style.display = "none";
    }
}

// 7. Poll Sweep Status
let sweepPollInterval = null;
function pollSweepStatus() {
    if (sweepPollInterval) return;
    
    const searchBtn = document.getElementById("start-search-btn");
    const progressText = document.getElementById("search-progress-text");
    
    sweepPollInterval = setInterval(async () => {
        try {
            const res = await fetch("/api/sweep-status");
            if (!res.ok) throw new Error();
            const data = await res.json();
            
            if (data.status === "RUNNING") {
                if (progressText) progressText.textContent = data.message;
            } else if (data.status === "SUCCESS") {
                appendSubmissionLog(`[SUCCESS] Sweep scan complete. Found and queued ${data.found} qualifying alphas.`);
                clearInterval(sweepPollInterval);
                sweepPollInterval = null;
                
                if (searchBtn) searchBtn.disabled = false;
                if (progressText) progressText.style.display = "none";
                
                loadSubmissionQueue();
                fetchPlatformStats();
                loadSubmissionRegistry();
            } else if (data.status === "ERROR") {
                appendSubmissionLog(`[ERROR] Sweep scan failed: ${data.message}`);
                clearInterval(sweepPollInterval);
                sweepPollInterval = null;
                
                if (searchBtn) searchBtn.disabled = false;
                if (progressText) progressText.style.display = "none";
            }
        } catch (e) {
            console.error("Error polling sweep status", e);
        }
    }, 1500);
}

// 8. Load registries (Green & Yellow lists)
async function loadSubmissionRegistry() {
    try {
        const greenRes = await fetch("/api/submitted-alphas");
        const yellowRes = await fetch("/api/yellow-alphas");
        
        if (!greenRes.ok || !yellowRes.ok) throw new Error("Failed to load registries");
        
        const greenAlphas = await greenRes.json();
        const yellowAlphas = await yellowRes.json();
        
        renderSubmissionRegistryTables(greenAlphas, yellowAlphas);
    } catch (e) {
        console.error("Failed to load registries", e);
    }
}

// 9. Render registries
function renderSubmissionRegistryTables(greenAlphas, yellowAlphas) {
    const greenBody = document.getElementById("sub-green-body");
    const yellowBody = document.getElementById("sub-yellow-body");
    
    // Update badge count based on active registry tab
    const activeTab = subActiveTab;
    const badgeText = document.getElementById("sub-registry-count");
    if (badgeText) {
        badgeText.textContent = `${activeTab === "green" ? greenAlphas.length : yellowAlphas.length} Alphas`;
    }
    
    // Render Green Table
    if (!greenBody) return;
    if (greenAlphas.length === 0) {
        greenBody.innerHTML = `<tr><td colspan="5" class="empty-state">No submitted alphas registered in green status.</td></tr>`;
    } else {
        greenBody.innerHTML = "";
        greenAlphas.forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>
                    <div style="font-weight: 700; color: #10b981; font-family: monospace;">${item.alpha_id}</div>
                    <div style="font-size: 0.7rem; color: var(--text-muted, #94a3b8); font-family: monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 250px;" title="${escapeHTML(item.formula)}">${escapeHTML(item.formula)}</div>
                </td>
                <td>${item.sharpe ? item.sharpe.toFixed(2) : "0.00"}</td>
                <td>${item.fitness ? item.fitness.toFixed(2) : "0.00"}</td>
                <td>${item.turnover ? item.turnover.toFixed(1) : "0.0"}%</td>
                <td style="font-size: 0.75rem; color: var(--text-muted, #94a3b8);">${item.submitted_at}</td>
            `;
            greenBody.appendChild(tr);
        });
    }
    
    // Render Yellow Table
    if (!yellowBody) return;
    if (yellowAlphas.length === 0) {
        yellowBody.innerHTML = `<tr><td colspan="5" class="empty-state">No permanently rejected alphas in yellow status.</td></tr>`;
    } else {
        yellowBody.innerHTML = "";
        yellowAlphas.forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>
                    <div style="font-weight: 700; color: #f59e0b; font-family: monospace;">${item.alpha_id}</div>
                    <div style="font-size: 0.7rem; color: var(--text-muted, #94a3b8); font-family: monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 180px;" title="${escapeHTML(item.formula)}">${escapeHTML(item.formula)}</div>
                </td>
                <td>${item.sharpe ? item.sharpe.toFixed(2) : "0.00"}</td>
                <td>${item.fitness ? item.fitness.toFixed(2) : "0.00"}</td>
                <td style="font-size: 0.75rem; color: #fca5a5; max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${escapeHTML(item.reason || '')}">${escapeHTML(item.reason || 'Correlation rejection')}</td>
                <td style="font-size: 0.75rem; color: var(--text-muted, #94a3b8);">${item.rejected_at}</td>
            `;
            yellowBody.appendChild(tr);
        });
    }
}

// Initialize Page
window.addEventListener("DOMContentLoaded", () => {
    // Add initial log line in memory
    appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[SYSTEM] Console initialized. Ready to receive log stream." });
    
    startEventStreams();
    fetchStats();
    pollSession();
    pollQueueStatus();
    pollInboxAlphas();

    // Wire up Nav Switcher Tabs
    const tabSimBtn = document.getElementById("tab-sim-btn");
    const tabSubmitBtn = document.getElementById("tab-submit-btn");
    const tabTriggerBtn = document.getElementById("tab-trigger-btn");
    const orchestratorView = document.getElementById("orchestrator-view");
    const submissionView = document.getElementById("submission-view");
    const triggerView = document.getElementById("trigger-view");
    
    if (tabSimBtn && tabSubmitBtn && tabTriggerBtn && orchestratorView && submissionView && triggerView) {
        tabSimBtn.addEventListener("click", () => {
            tabSimBtn.style.background = "linear-gradient(135deg, rgba(6,182,212,0.2), rgba(59,130,246,0.2))";
            tabSimBtn.style.borderColor = "rgba(6,182,212,0.4)";
            tabSimBtn.style.color = "white";
            
            tabSubmitBtn.style.background = "none";
            tabSubmitBtn.style.borderColor = "transparent";
            tabSubmitBtn.style.color = "#94a3b8";

            tabTriggerBtn.style.background = "none";
            tabTriggerBtn.style.borderColor = "transparent";
            tabTriggerBtn.style.color = "#94a3b8";
            
            orchestratorView.style.display = "block";
            submissionView.style.display = "none";
            triggerView.style.display = "none";
        });
        
        tabSubmitBtn.addEventListener("click", () => {
            tabSubmitBtn.style.background = "linear-gradient(135deg, rgba(16,185,129,0.2), rgba(5,150,105,0.2))";
            tabSubmitBtn.style.borderColor = "rgba(16,185,129,0.4)";
            tabSubmitBtn.style.color = "white";
            
            tabSimBtn.style.background = "none";
            tabSimBtn.style.borderColor = "transparent";
            tabSimBtn.style.color = "#94a3b8";

            tabTriggerBtn.style.background = "none";
            tabTriggerBtn.style.borderColor = "transparent";
            tabTriggerBtn.style.color = "#94a3b8";
            
            orchestratorView.style.display = "none";
            submissionView.style.display = "block";
            triggerView.style.display = "none";
            
            // Initial load for submission view
            fetchPlatformStats();
            loadSubmissionQueue();
            loadSubmissionRegistry();
        });

        tabTriggerBtn.addEventListener("click", () => {
            tabTriggerBtn.style.background = "linear-gradient(135deg, rgba(6,182,212,0.2), rgba(59,130,246,0.2))";
            tabTriggerBtn.style.borderColor = "rgba(6,182,212,0.4)";
            tabTriggerBtn.style.color = "white";
            
            tabSimBtn.style.background = "none";
            tabSimBtn.style.borderColor = "transparent";
            tabSimBtn.style.color = "#94a3b8";

            tabSubmitBtn.style.background = "none";
            tabSubmitBtn.style.borderColor = "transparent";
            tabSubmitBtn.style.color = "#94a3b8";
            
            orchestratorView.style.display = "none";
            submissionView.style.display = "none";
            triggerView.style.display = "block";

            // Poll active trigger status once on activation
            pollTriggerStatus();
        });
    }

    // Wire up Search & Submission Controls
    const startSearchBtn = document.getElementById("start-search-btn");
    if (startSearchBtn) {
        startSearchBtn.addEventListener("click", startSearch);
    }
    
    const bulkSubmitBtn = document.getElementById("bulk-submit-btn");
    if (bulkSubmitBtn) {
        bulkSubmitBtn.addEventListener("click", () => {
            const chkboxes = document.querySelectorAll(".queue-row-chk:checked");
            const ids = Array.from(chkboxes).map(cb => cb.getAttribute("data-id"));
            triggerSubmission(ids);
        });
    }
    
    const queueSelectAll = document.getElementById("queue-select-all");
    if (queueSelectAll) {
        queueSelectAll.addEventListener("change", (e) => {
            const checked = e.target.checked;
            document.querySelectorAll(".queue-row-chk").forEach(cb => {
                cb.checked = checked;
            });
        });
    }
    
    const queueSearchInput = document.getElementById("queue-search-input");
    if (queueSearchInput) {
        queueSearchInput.addEventListener("input", renderSubmissionQueueTable);
    }
    
    const subTabBtns = document.querySelectorAll(".sub-tab-btn");
    const subGreenTable = document.getElementById("sub-green-table");
    const subYellowTable = document.getElementById("sub-yellow-table");
    
    subTabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            subTabBtns.forEach(b => {
                b.classList.remove("active");
                b.style.background = "none";
                b.style.borderColor = "transparent";
                b.style.color = "#94a3b8";
            });
            btn.classList.add("active");
            subActiveTab = btn.getAttribute("data-tab");
            
            // Set styles for active registry tab
            if (subActiveTab === "green") {
                btn.style.background = "linear-gradient(135deg, rgba(16,185,129,0.2), rgba(5,150,105,0.2))";
                btn.style.borderColor = "rgba(16,185,129,0.4)";
                btn.style.color = "white";
                if (subGreenTable) subGreenTable.style.display = "table";
                if (subYellowTable) subYellowTable.style.display = "none";
            } else {
                btn.style.background = "linear-gradient(135deg, rgba(245,158,11,0.2), rgba(245,158,11,0.2))";
                btn.style.borderColor = "rgba(245,158,11,0.4)";
                btn.style.color = "white";
                if (subGreenTable) subGreenTable.style.display = "none";
                if (subYellowTable) subYellowTable.style.display = "table";
            }
            loadSubmissionRegistry();
        });
    });

    // Wire up Review Inbox Controls
    const inboxPushAllBtn = document.getElementById("inbox-push-all-btn");
    if (inboxPushAllBtn) {
        inboxPushAllBtn.addEventListener("click", pushAllInbox);
    }
    const inboxClearBtn = document.getElementById("inbox-clear-btn");
    if (inboxClearBtn) {
        inboxClearBtn.addEventListener("click", clearInbox);
    }

    // Wire up Alpha Vault Tabs
    const vaultTabBtns = document.querySelectorAll(".vault-tab-btn");
    vaultTabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            vaultTabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            activeVaultTab = btn.getAttribute("data-tab");
            renderVaultTable();
        });
    });

    // Wire up Alpha Vault Search
    const vaultSearchInput = document.getElementById("vault-search-input");
    if (vaultSearchInput) {
        vaultSearchInput.addEventListener("input", (e) => {
            vaultSearchQuery = e.target.value;
            renderVaultTable();
        });
    }
    
    // Poll sweep status if already running on load
    pollSweepStatus();
    // Poll submission status if already running on load
    pollSubmissionStatus();
    
    // Update platform stats every 10 seconds if submission view is open
    setInterval(() => {
        const submissionView = document.getElementById("submission-view");
        if (submissionView && submissionView.style.display === "block") {
            fetchPlatformStats();
            loadSubmissionQueue();
        }
    }, 10000);
    
    // Poll stats table updates every 20 seconds to reduce API requests
    statsInterval = setInterval(fetchStats, 20000);
    // Poll WQ Session status every 15 seconds
    setInterval(pollSession, 15000);
    // Poll active backtesting queue every 2 seconds
    setInterval(pollQueueStatus, 2000);
    // Poll review inbox queue every 2 seconds
    setInterval(pollInboxAlphas, 2000);

    // ==========================================
    // TRIGGER FLOW CLIENT CONTROLLER
    // ==========================================
    const trigDatasetInput = document.getElementById("trig-dataset-input");
    const trigCountInput = document.getElementById("trig-count-input");
    const trigGeminiInput = document.getElementById("trig-gemini-input");
    const trigLaunchBtn = document.getElementById("trig-launch-btn");
    const trigProgressBarContainer = document.getElementById("trig-progress-bar-container");
    const trigProgressBar = document.getElementById("trig-progress-bar");
    const trigCurrentStepLabel = document.getElementById("trig-current-step-label");
    const trigPercentLabel = document.getElementById("trig-percent-label");
    const trigLogConsole = document.getElementById("trig-log-console");

    const trigStatusText = document.getElementById("trig-status-text");
    const trigDatasetText = document.getElementById("trig-dataset-text");
    const trigCountText = document.getElementById("trig-count-text");
    const trigProgressText = document.getElementById("trig-progress-text");

    let triggerPollInterval = null;
    let triggerLastLogLength = 0;

    function renderTriggerLogLine(text) {
        if (triggerLastLogLength === 0) {
            trigLogConsole.innerHTML = "";
        }
        const lineDiv = document.createElement("div");
        lineDiv.style.marginBottom = "4px";
        lineDiv.style.lineHeight = "1.4";
        
        if (text.includes("[ERROR]")) {
            lineDiv.style.color = "#ef4444"; // red
        } else if (text.includes("[WARNING]")) {
            lineDiv.style.color = "#fbbf24"; // yellow
        } else if (text.includes("SUCCESS")) {
            lineDiv.style.color = "#10b981"; // green
        } else {
            lineDiv.style.color = "#a5f3fc"; // cyan
        }
        
        lineDiv.textContent = text;
        trigLogConsole.appendChild(lineDiv);
        trigLogConsole.scrollTop = trigLogConsole.scrollHeight;
    }

    function updateStepChecklist(stepNum, status) {
        const item = document.getElementById(`trig-step-${stepNum}`);
        const icon = document.getElementById(`trig-step-${stepNum}-icon`);
        
        if (!item || !icon) return;

        if (status === "pending") {
            icon.textContent = "⚪";
            icon.style.animation = "";
            item.style.color = "var(--text-muted, #94a3b8)";
        } else if (status === "running") {
            icon.textContent = "⏳";
            icon.style.animation = "pulse 1.2s infinite";
            item.style.color = "#38bdf8";
        } else if (status === "completed") {
            icon.textContent = "✅";
            icon.style.animation = "";
            item.style.color = "#10b981";
        } else if (status === "error") {
            icon.textContent = "❌";
            icon.style.animation = "";
            item.style.color = "#ef4444";
        }
    }

    async function pollTriggerStatus() {
        try {
            const res = await fetch("/api/trigger-status");
            if (!res.ok) return;
            const data = await res.json();

            // Update stats cards
            trigStatusText.textContent = data.status || "IDLE";
            if (data.status === "RUNNING") {
                trigStatusText.style.color = "#38bdf8";
            } else if (data.status === "SUCCESS") {
                trigStatusText.style.color = "#10b981";
            } else if (data.status === "ERROR") {
                trigStatusText.style.color = "#ef4444";
            } else {
                trigStatusText.style.color = "";
            }

            trigDatasetText.textContent = data.dataset || "None";
            trigCountText.textContent = `${data.generated_count || 0} / ${data.target_count || 0}`;
            trigProgressText.textContent = `${data.progress_percent || 0}%`;

            // Update progress bar
            if (data.status === "RUNNING" || data.status === "SUCCESS" || data.status === "ERROR") {
                trigProgressBarContainer.style.display = "block";
                trigProgressBar.style.width = `${data.progress_percent || 0}%`;
                trigPercentLabel.textContent = `${data.progress_percent || 0}%`;
                trigCurrentStepLabel.textContent = data.current_step || "Executing sequence";
            }

            const progress = data.progress_percent || 0;
            const status = data.status || "IDLE";

            if (status === "RUNNING") {
                trigLaunchBtn.disabled = true;
                trigLaunchBtn.innerHTML = `⚙️ Sequencer Active (${progress}%)`;
                trigLaunchBtn.style.background = "linear-gradient(135deg, rgba(6,182,212,0.4), rgba(59,130,246,0.4))";

                if (progress < 15) {
                    updateStepChecklist(1, "running");
                    [2, 3, 4, 5].forEach(i => updateStepChecklist(i, "pending"));
                } else if (progress < 30) {
                    updateStepChecklist(1, "completed");
                    updateStepChecklist(2, "running");
                    [3, 4, 5].forEach(i => updateStepChecklist(i, "pending"));
                } else if (progress < 85) {
                    updateStepChecklist(1, "completed");
                    updateStepChecklist(2, "completed");
                    updateStepChecklist(3, "running");
                    [4, 5].forEach(i => updateStepChecklist(i, "pending"));
                } else if (progress < 90) {
                    updateStepChecklist(1, "completed");
                    updateStepChecklist(2, "completed");
                    updateStepChecklist(3, "completed");
                    updateStepChecklist(4, "running");
                    updateStepChecklist(5, "pending");
                } else {
                    updateStepChecklist(1, "completed");
                    updateStepChecklist(2, "completed");
                    updateStepChecklist(3, "completed");
                    updateStepChecklist(4, "completed");
                    updateStepChecklist(5, "running");
                }
            } else if (status === "SUCCESS") {
                if (triggerPollInterval) {
                    clearInterval(triggerPollInterval);
                    triggerPollInterval = null;
                }

                [1, 2, 3, 4, 5].forEach(i => updateStepChecklist(i, "completed"));

                trigLaunchBtn.disabled = false;
                trigLaunchBtn.innerHTML = `✅ Synthesis Succeeded!`;
                trigLaunchBtn.style.background = "linear-gradient(135deg, #10b981, #059669)";

                pollInboxAlphas();
                pollQueueStatus();

                setTimeout(() => {
                    trigLaunchBtn.innerHTML = `🚀 LAUNCH ALPHA FORGE SEQUENCER`;
                    trigLaunchBtn.style.background = "";
                }, 3000);
            } else if (status === "ERROR") {
                if (triggerPollInterval) {
                    clearInterval(triggerPollInterval);
                    triggerPollInterval = null;
                }

                if (progress < 15) updateStepChecklist(1, "error");
                else if (progress < 30) { updateStepChecklist(1, "completed"); updateStepChecklist(2, "error"); }
                else if (progress < 85) { updateStepChecklist(1, "completed"); updateStepChecklist(2, "completed"); updateStepChecklist(3, "error"); }
                else if (progress < 90) { updateStepChecklist(1, "completed"); updateStepChecklist(2, "completed"); updateStepChecklist(3, "completed"); updateStepChecklist(4, "error"); }
                else { [1, 2, 3, 4].forEach(i => updateStepChecklist(i, "completed")); updateStepChecklist(5, "error"); }

                trigLaunchBtn.disabled = false;
                trigLaunchBtn.innerHTML = `❌ Synthesis Failed`;
                trigLaunchBtn.style.background = "linear-gradient(135deg, #ef4444, #dc2626)";

                setTimeout(() => {
                    trigLaunchBtn.innerHTML = `🚀 LAUNCH ALPHA FORGE SEQUENCER`;
                    trigLaunchBtn.style.background = "";
                }, 3000);
            }

            if (data.logs && data.logs.length > triggerLastLogLength) {
                for (let i = triggerLastLogLength; i < data.logs.length; i++) {
                    renderTriggerLogLine(data.logs[i]);
                }
                triggerLastLogLength = data.logs.length;
            }

        } catch (e) {
            console.error("Trigger polling error:", e);
        }
    }

    async function launchTriggerFlow() {
        const dataset = trigDatasetInput.value.trim();
        const count = parseInt(trigCountInput.value);
        const geminiKey = trigGeminiInput.value.trim();

        if (!dataset) {
            alert("Please provide a dataset search name (e.g. analyst10)!");
            return;
        }

        if (isNaN(count) || count < 5) {
            alert("Please target at least 5 alphas!");
            return;
        }

        trigLaunchBtn.disabled = true;
        trigLaunchBtn.innerHTML = `⚙️ Preparing Pipeline...`;
        
        triggerLastLogLength = 0;
        trigLogConsole.innerHTML = "";
        renderTriggerLogLine("[SYSTEM] Initializing background trigger sequence connection...");
        
        [1, 2, 3, 4, 5].forEach(i => updateStepChecklist(i, "pending"));

        try {
            const res = await fetch("/api/trigger-flow", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    dataset: dataset,
                    count: count,
                    gemini_key: geminiKey
                })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || `HTTP ${res.status}`);
            }

            renderTriggerLogLine("[SYSTEM] Sequencer booted. Background worker thread launched successfully.");
            
            if (triggerPollInterval) clearInterval(triggerPollInterval);
            triggerPollInterval = setInterval(pollTriggerStatus, 2000);
            pollTriggerStatus();
            
        } catch (e) {
            renderTriggerLogLine(`[ERROR] Boot failed: ${e.message}`);
            trigLaunchBtn.disabled = false;
            trigLaunchBtn.innerHTML = `🚀 LAUNCH ALPHA FORGE SEQUENCER`;
            alert(`Failed to boot Trigger Flow:\n${e.message}`);
        }
    }

    if (trigLaunchBtn) {
        trigLaunchBtn.addEventListener("click", launchTriggerFlow);
    }
    
    // Auto-resume trigger telemetry polling on reload if active
    fetch("/api/trigger-status")
        .then(r => r.json())
        .then(data => {
            if (data.status === "RUNNING") {
                triggerLastLogLength = 0;
                if (triggerPollInterval) clearInterval(triggerPollInterval);
                triggerPollInterval = setInterval(pollTriggerStatus, 2000);
                pollTriggerStatus();
            }
        }).catch(err => {});
});

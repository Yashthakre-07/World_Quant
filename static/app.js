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
const submittedTableBody = document.querySelector("#submitted-table tbody");

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
    
    // Search query match
    if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return log.message.toLowerCase().includes(query) || 
               log.timestamp.toLowerCase().includes(query) || 
               log.type.toLowerCase().includes(query);
    }
    
    return true;
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
        <span class="log-text">${escapeHTML(displayMsg)}</span>
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

        // Update Submissions Registry Table
        if (data.submitted_list && data.submitted_list.length > 0) {
            submittedTableBody.innerHTML = "";
            data.submitted_list.forEach(item => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td style="font-family: 'Fira Code', monospace; font-size: 0.75rem;">${item.alpha_id}</td>
                    <td class="text-danger-red" style="font-weight: 700;">${Number(item.sharpe).toFixed(2)} <span class="badge badge-danger-red" style="margin-left: 6px;">SUBMITTABLE</span></td>
                    <td style="font-weight: 500;">${Number(item.fitness).toFixed(2)}</td>
                    <td>${Number(item.turnover).toFixed(1)}%</td>
                    <td><a href="${item.alpha_link}" target="_blank" class="action-link red-action">Submit on platform ↗</a></td>
                `;
                submittedTableBody.appendChild(tr);
            });
        } else {
            submittedTableBody.innerHTML = `<tr><td colspan="5" class="empty-state">No successful submissions logged yet.</td></tr>`;
        }
    } catch (e) {
        console.error("Failed to fetch stats summary", e);
    }
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
        const sessionTimer = document.getElementById("session-timer");
        const sessionBadge = document.getElementById("session-status");
        if (!r.ok) {
            if (sessionTimer) sessionTimer.textContent = "Session Error";
            return;
        }
        const data = await r.json();
        if (data.error) {
            if (sessionTimer) sessionTimer.textContent = "No Session";
            if (sessionBadge) {
                sessionBadge.className = "session-badge expired";
            }
            return;
        }
        if (data.expired) {
            if (sessionTimer) sessionTimer.textContent = "Session Expired";
            if (sessionBadge) {
                sessionBadge.className = "session-badge expired";
            }
        } else {
            const mins = Math.floor(data.remaining_seconds / 60);
            const hrs = Math.floor(mins / 60);
            const displayTime = hrs > 0 ? `${hrs}h ${mins % 60}m remaining` : `${mins}m remaining`;
            if (sessionTimer) sessionTimer.textContent = `Session Live: ${displayTime}`;
            if (sessionBadge) {
                sessionBadge.className = "session-badge live";
            }
        }
        }
    } catch (e) {
        console.error("Error polling session status", e);
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
            const isSimulating = alpha.status === "SIMULATING" ? "simulating" : "";
            card.className = `alpha-card ${isSimulating}`;
            
            const sharpeVal = alpha.sharpe !== null ? Number(alpha.sharpe).toFixed(2) : "-";
            const fitnessVal = alpha.fitness !== null ? Number(alpha.fitness).toFixed(2) : "-";
            const turnoverVal = alpha.turnover !== null ? Number(alpha.turnover).toFixed(1) + "%" : "-";
            
            let statusBadgeClass = "badge-info";
            if (alpha.status === "SUBMITTED") statusBadgeClass = "badge-success";
            else if (alpha.status === "SIMULATING") statusBadgeClass = "badge-warning";
            else if (alpha.status === "EVALUATING") statusBadgeClass = "badge-primary";
            else if (["HARD_REJECT", "SOFT_FAIL", "ERROR"].includes(alpha.status)) statusBadgeClass = "badge-danger";
            
            const descText = alpha.error_message ? `<span class="text-danger-red">${alpha.error_message}</span>` : alpha.hypothesis;
            
            card.innerHTML = `
                <div class="alpha-card-header">
                    <span class="alpha-card-family">#${index + 1}: ${escapeHTML(alpha.family)}</span>
                    <span class="badge ${statusBadgeClass}">${alpha.status}</span>
                </div>
                <div class="alpha-card-formula">${escapeHTML(alpha.formula)}</div>
                <div class="alpha-card-meta">
                    <span style="font-size: 0.7rem; max-width: 60%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${escapeHTML(descText)}</span>
                    <div class="alpha-card-metrics">
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

// Initialize Page
window.addEventListener("DOMContentLoaded", () => {
    // Add initial log line in memory
    appendLog({ timestamp: new Date().toLocaleTimeString(), message: "[SYSTEM] Console initialized. Ready to receive log stream." });
    
    startEventStreams();
    fetchStats();
    pollSession();
    pollQueueStatus();
    
    // Poll stats table updates every 20 seconds to reduce API requests
    statsInterval = setInterval(fetchStats, 20000);
    // Poll WQ Session status every 15 seconds
    setInterval(pollSession, 15000);
    // Poll active backtesting queue every 2 seconds
    setInterval(pollQueueStatus, 2000);
});

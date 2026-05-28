# 🚀 AlphaForge: Autonomous Quantitative Research Pipeline

Welcome to **AlphaForge**! This repository is an industrial-grade, 24/7 autonomous quantitative research pipeline designed to generate, validate, backtest, and submit high-fitness formulaic alphas to the **WorldQuant Brain** platform.

This document serves as a **Permanent Onboarding Guide for Developers and Future AI Coding Assistants**. If you are a new AI agent loading this workspace, read this document, along with `instructions.md` and `research.md`, before executing any commands or making changes.

---

## 🏗️ 1. Pipeline Architecture Map

```mermaid
graph TD
    subgraph Local Development PC
        DC[desktop_control.py] -->|Secure REST API| RS_Sai
        DC -->|Secure REST API| RS_Yash
    end

    subgraph Live Cloud Servers (Render)
        RS_Sai[world-quant.onrender.com <br/> Sai Profile: saineela731@gmail.com]
        RS_Yash[world-quant-1.onrender.com <br/> Yash Profile: beyondsynapse@gmail.com]
    end

    subgraph WorldQuant Brain Cluster
        RS_Sai -->|Simulation Queue| WQ_Sai[WQ Account 1 <br/> Cap: 3 Concurrent Sims]
        RS_Yash -->|Simulation Queue| WQ_Yash[WQ Account 2 <br/> Cap: 3 Concurrent Sims]
    end

    subgraph Local Data & Logs
        DB[(db/alpha_vault.db)]
        Q[db/simulation_queue.json]
        IB[db/inbox_queue.json]
    end

    run_pipeline.py --> DB
    run_pipeline.py --> Q
    run_pipeline.py --> IB
```

---

## 🔑 2. The 3 Golden Rules (Strict Platform Compliance)

WorldQuant Brain enforces strict rate limits. Breaking these rules will result in account lockout or IP blocks:

1.  **Strict Concurrency Lock (Max 3 Batch Workers - 30 Alphas Concurrent)**: The queue runner utilizes WorldQuant's Multi-Simulation API. It groups regular alphas into batches of up to 10. The executor is locked at a limit of **3 concurrent batches**, which simulates up to **30 alphas simultaneously** while remaining strictly compliant with WQ's 3-slot platform active limit.
2.  **Mandatory 5-Second Batch Spacing**: All API batch submissions to the simulations endpoint are locked. The runner must sleep for at least **5 seconds** between batch POST requests to prevent IP rate locks and HTTP 429 limits.
3.  **Local Validation First**: All proposed alpha formulas **must** pass through `src/validator.py` locally before hitting the live WorldQuant network. Mismatched brackets, Python operators (`and`/`or`), or invalid fields must be rejected instantly.

---

## 👥 3. Multi-Profile Environment Configuration

AlphaForge is fully profile-aware and dynamically switches credentials to support two distinct research pipelines:

*   **Sai's Profile**:
    *   **Env File**: `sai.env` (loaded dynamically when running for Sai)
    *   **Render Server**: `https://world-quant.onrender.com`
    *   **API Token**: `yashthakreop`
    *   **Cookies**: Saved on disk as `db/session_cookies_saineela731_gmail_com.json`
*   **Yash's Profile**:
    *   **Env File**: `yash.env` (loaded dynamically when running for Yash)
    *   **Render Server**: `https://world-quant-1.onrender.com`
    *   **API Token**: `yashthakreop1`
    *   **Cookies**: Saved on disk as `db/session_cookies_beyondsynapse_gmail_com.json`

> [!IMPORTANT]
> **Dynamic Credential Resolution**: `src/auth.py` resolves credentials dynamically at runtime. Never statically import environment configuration, as it will corrupt session token validation.

---

## 📁 4. Core Directory & Script Manifest

*   `run_pipeline.py`: The core orchestrator. Runs the Flask web dashboard, handles the background worker pool using `simulate_batch` for WQ Multi-Simulations, executes the queued batches, and manages self-healing auth and SQLite status updates.
*   `src/auth.py`: The secure custom `requests.Session` subclass. Manages automatic JWT token decoding, dynamic cookie caching, and multi-process authentication.
*   `desktop_control.py`: An interactive, zero-dependency local CLI tool that connects securely to the Render servers to push formulas, read telemetry, download generated vault alphas, and check pipeline status.
*   `trigger_generator.py`: A command-line script to systematically generate 200 combinatorial alphas per dataset and securely push them to the console's "Review Inbox" using the secure Bearer token.
*   `alpha_generation_guide.md`: A comprehensive cookbook containing WQ FastExpr operators cheat sheet, 20 momentum, mean reversion, and price-volume templates, and tuning directions.
*   `research.md`: The quantitative research log. Documents in-sample Sharpe ratio sweet spots, decay selections, turnover optimization guides, and successful Alpha Catalogs (Generations 1 to 4).
*   `instructions.md`: The developer manual and SQLite schema directory. Contains all SQLite tables, endpoints, and quick-start command references.

---

## 🤖 5. Playbook for Future AI Coding Assistants

If you are an AI agent loaded into this repository to continue this task, execute the following steps sequentially to gain immediate, flawless context:

1.  **Read the Research Manifests First**:
    *   Open and fully review [research.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/research.md) to understand current high-fitness alpha formulas.
    *   Open and fully review [instructions.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/instructions.md) to understand SQLite tables, API schemas, and pipeline endpoints.
    *   Open and review the simplified dataset catalog in [dataset.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/dataset.md).
    *   Open and review the combinatorial generator guide in [alpha_generation_guide.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/alpha_generation_guide.md).
    *   *If you have any doubt, always use the official ACE API package* unzipped in [ace_api_extracted](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/ace_api_extracted) since it contains the official WQ documentation and files on how to use everything.
2.  **Verify Server Telemetry**:
    *   Run `python scratch_query_sai.py` to pull down the live session state and queue status from the active Render server and inspect the generated `sai_server_report.json`.
3.  **Validate Locally**:
    *   Always test any proposed formula by running `python -c "from src.validator import validate_fastexpr; print(validate_fastexpr('<YOUR_FORMULA>'))"` to guarantee syntax correctness before proposing a backtest.
4.  **Always Update the Manuals**:
    *   If you find a new math anomaly, optimize a decay setting, or fix a backend bug, immediately log it at the end of `research.md` or `instructions.md`. Keep this repository self-documenting!

#!/usr/bin/env python3
"""
WQ Alpha Forge - Standalone Terminal Trigger File
------------------------------------------------
This script runs the entire alpha generation and submission flow from the terminal.

How to use:
    python run_trigger.py --dataset analyst10 --count 200
"""

import os
import sys
import json
import argparse
import time
import re
import random
from pathlib import Path

# Monkeypatch requests to bypass Windows SSL verification issues globally
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
orig_request = requests.Session.request
def new_request(self, *args, **kwargs):
    kwargs['verify'] = False
    return orig_request(self, *args, **kwargs)
requests.Session.request = new_request


# Add project root and documentation/ace_api_extracted to path
WQ_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(WQ_ROOT))
ACE_LIB_DIR = WQ_ROOT / "documentation" / "ace_api_extracted"
sys.path.insert(0, str(ACE_LIB_DIR))

# Try importing src.config and ace_lib
try:
    from src.config import GEMINI_API_KEY, DB_DIR, API_SECRET_TOKEN, SERVER_HOST, SERVER_PORT
except ImportError:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    DB_DIR = WQ_ROOT / "db"
    API_SECRET_TOKEN = os.environ.get("API_SECRET_TOKEN", "wq-default-token-change-me")
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 8000

try:
    import ace_lib
except ImportError:
    print("[ERROR] Could not import ace_lib. Ensure the ace_api_extracted folder is present.")
    sys.exit(1)

# Helper to load environmental variables from sai.env or yash.env
def load_secrets():
    # Load dotenv if available
    try:
        from dotenv import load_dotenv
        for env_name in ["sai.env", "yash.env", ".env"]:
            env_path = WQ_ROOT / env_name
            if env_path.exists():
                load_dotenv(env_path, override=True)
                break
    except ImportError:
        pass


def run_trigger_flow(dataset_name: str, count: int, token: str = None, gemini_key: str = None, logger_callback=None):
    def log(msg, level="INFO"):
        full_msg = f"[{time.strftime('%H:%M:%S')}] [{level}] {msg}"
        print(full_msg)
        if logger_callback:
            logger_callback(msg, level)

    log("=" * 60)
    log(f"Starting Alpha Forge Trigger Flow for dataset '{dataset_name}' (Target: {count} alphas)...")
    log("=" * 60)

    # 1. Credentials setup
    load_secrets()
    if os.getenv("WQ_EMAIL"):
        os.environ["BRAIN_CREDENTIAL_EMAIL"] = os.getenv("WQ_EMAIL")
    if os.getenv("WQ_PASSWORD"):
        os.environ["BRAIN_CREDENTIAL_PASSWORD"] = os.getenv("WQ_PASSWORD")
    active_token = token or os.getenv("API_SECRET_TOKEN", API_SECRET_TOKEN)
    active_gemini_key = gemini_key or os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)

    # 2. Start ace_lib session
    log("Step 1: Connecting to WorldQuant BRAIN via ace_lib...")
    try:
        session = ace_lib.start_session()
        log("Session successfully started and verified.")
    except Exception as e:
        log(f"Failed to start WQ session via ace_lib: {e}", "ERROR")
        return False, str(e)

    # 3. Fetch fields and operators
    log(f"Step 2: Fetching fields for dataset '{dataset_name}'...")
    try:
        fields_df = ace_lib.get_datafields(
            session,
            instrument_type="EQUITY",
            region="USA",
            delay=1,
            universe="TOP3000",
            search=dataset_name,
        )
        if fields_df.empty:
            log(f"No fields found for dataset search name '{dataset_name}'. Using fallback generic fields.", "WARNING")
            fields = [{"id": f"{dataset_name}_eps_smart", "description": "Fallback generic EPS estimate"}]
        else:
            fields = fields_df.to_dict("records")
            log(f"Successfully fetched {len(fields)} fields from WorldQuant BRAIN.")
    except Exception as e:
        log(f"Error fetching data fields: {e}. Falling back to default list.", "WARNING")
        fields = [{"id": f"{dataset_name}_eps_smart", "description": "Fallback eps"}]

    log("Fetching available mathematical operators...")
    try:
        operators_df = ace_lib.get_operators(session)
        operators = operators_df.to_dict("records")
        log(f"Fetched {len(operators)} mathematical operators.")
    except Exception as e:
        log(f"Error fetching operators: {e}", "WARNING")
        operators = []

    # 4. Save metadata to registry
    alpha_dataset_dir = WQ_ROOT / "alphas_dataset" / dataset_name / "alphas"
    alpha_dataset_dir.mkdir(parents=True, exist_ok=True)
    
    log(f"Saving fetched fields and operators to metadata registry inside: alphas_dataset/{dataset_name}/alphas/")
    with open(alpha_dataset_dir / "fields.json", "w", encoding="utf-8") as f:
        json.dump(fields, f, indent=2)
    with open(alpha_dataset_dir / "operators.json", "w", encoding="utf-8") as f:
        json.dump(operators, f, indent=2)

    # 5. Hybrid Alpha Formula Generation
    log("Step 3: Initiating AI Alpha Generation Sequence...")
    field_ids = [fd["id"] for fd in fields]
    
    # Let's try to initialize Gemini
    gemini_active = False
    if active_gemini_key and active_gemini_key.strip().lower() not in ("none", "disable", ""):
        try:
            import google.generativeai as genai
            genai.configure(api_key=active_gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            gemini_active = True
            log("Gemini API successfully configured. Crafting quantitative trading hypotheses...")
        except Exception as e:
            log(f"Failed to load google.generativeai or connect: {e}. Switching to rule-based combinatorial generator.", "WARNING")

    blueprints = []
    
    if gemini_active:
        # Prompt Gemini to design 10 tailored alpha blueprints for these specific fields
        fields_summary = "\n".join([f"- Field ID: {fd.get('id')} | Description: {fd.get('description', '')}" for fd in fields[:25]])
        prompt = f"""
You are an expert quantitative finance researcher designing statistical arbitrage alphas for WorldQuant BRAIN.
We have just fetched a new dataset called '{dataset_name}' containing these fields:
{fields_summary}

Task: Design exactly 10 WQ FastExpr alpha templates (blueprints) matching these fields.
Use classic WQ operators: rank, zscore, ts_delta, ts_decay_linear, ts_mean, ts_std_dev, group_neutralize, trade_when, ts_corr, ts_regression.

For each blueprint, use placeholder markers like:
- {{F}} to represent a primary dataset field.
- {{F2}} to represent a secondary composite dataset field (if appropriate).
- {{D}} for lookback days (e.g. 5, 10, 20, 63).
- {{G}} for neutralizing group (e.g. industry, subindustry).

Return the blueprints in structured XML/JSON-like blocks. Focus on different quantitative themes:
1. Reversion
2. Momentum / Trend Following
3. Volatility-Gated Reversion
4. Cross-Field composite
5. Volume interactive (using standard fields like close, volume, returns, cap, adv20)

OUTPUT ONLY a JSON array of templates like this:
[
  {{"theme": "Gated Reversion", "template": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear({{F}}, {{D}})), 0), {{G}})"}},
  ...
]
Do NOT return extra conversational text. Output ONLY valid JSON.
"""
        try:
            r = model.generate_content(prompt)
            clean_text = r.text.strip()
            # Clean markdown codeblocks
            clean_text = re.sub(r'```json\s*', '', clean_text)
            clean_text = re.sub(r'\s*```', '', clean_text)
            
            blueprints = json.loads(clean_text)
            log(f"Gemini successfully engineered {len(blueprints)} custom alpha blueprints tailored for {dataset_name}!")
        except Exception as e:
            log(f"Failed to generate blueprints with Gemini: {e}. Falling back to default blueprints.", "WARNING")
            blueprints = []

    # Fallback / Default blueprints if Gemini didn't run or failed
    if not blueprints:
        log("Using robust predefined qualitative trading models...")
        blueprints = [
            {"theme": "Revision Reversion", "template": "-rank(ts_delta({F}, {D}))"},
            {"theme": "Decay Momentum", "template": "group_neutralize(ts_decay_linear(ts_delta({F}, {D}), {D}), {G})"},
            {"theme": "Mean Reversion", "template": "-rank({F} - ts_mean({F}, {D}))"},
            {"theme": "Volatility Adjusted Deviation", "template": "-ts_decay_linear(({F} - ts_mean({F}, {D})) / (ts_std_dev({F}, {D}) + 0.001), {D})"},
            {"theme": "Group Neutral Reversion", "template": "-group_zscore({F}, {G})"},
            {"theme": "Cross-Field Delta Composite", "template": "rank(ts_delta({F}, {D})) - rank(ts_delta({F2}, {D}))"},
            {"theme": "Volume Interaction Momentum", "template": "ts_corr(rank({F}), rank(returns), {D})"},
            {"theme": "Conditional Volume Gating", "template": "trade_when(volume > adv20 * 0.5, -rank(ts_decay_linear({F}, {D})), 0)"},
            {"theme": "OLS Trend Neutralization", "template": "group_neutralize(ts_regression({F}, {F}, {D}), {G})"},
            {"theme": "Double-Smooth Composite", "template": "group_neutralize(ts_decay_linear(ts_decay_linear(rank({F}) + rank(-{F2}), 5), {D}), {G})"}
        ]

    # Generate alphas based on templates
    log(f"Expanding blueprints into {count} unique mathematical candidate alphas...")
    generated_configs = []
    seen_formulas = set()
    
    lookbacks = [5, 10, 15, 20, 22, 30, 40, 60, 126, 252]
    groups = ["industry", "subindustry"]
    settings_variants = [
        {"decay": 0, "neutralization": "SUBINDUSTRY", "truncation": 0.08},
        {"decay": 3, "neutralization": "SUBINDUSTRY", "truncation": 0.08},
        {"decay": 5, "neutralization": "SUBINDUSTRY", "truncation": 0.08},
        {"decay": 10, "neutralization": "SUBINDUSTRY", "truncation": 0.08},
        {"decay": 0, "neutralization": "INDUSTRY", "truncation": 0.08},
        {"decay": 5, "neutralization": "INDUSTRY", "truncation": 0.05},
    ]

    attempts = 0
    max_attempts = count * 20
    
    while len(generated_configs) < count and attempts < max_attempts:
        attempts += 1
        bp = random.choice(blueprints)
        template = bp["template"]
        
        # Pick fields
        f1 = random.choice(field_ids)
        f2 = random.choice(field_ids) if len(field_ids) > 1 else f1
        if f1 == f2 and len(field_ids) > 1:
            f2 = random.choice([x for x in field_ids if x != f1])
            
        d = random.choice(lookbacks)
        g = random.choice(groups)
        
        # Format formula
        formula = template.replace("{F}", f1).replace("{F2}", f2).replace("{D}", str(d)).replace("{G}", g)
        formula = formula.replace(" ", "")  # Clean spaces
        
        if formula in seen_formulas:
            continue
            
        seen_formulas.add(formula)
        
        # Choose simulation setting
        sv = random.choice(settings_variants)
        idx = len(generated_configs) + 1
        
        alpha_obj = {
            "name": f"G_{dataset_name}_{idx:03d}",
            "type": "REGULAR",
            "settings": {
                "instrumentType": "EQUITY",
                "region": "USA",
                "universe": "TOP3000",
                "delay": 1,
                "decay": sv["decay"],
                "neutralization": sv["neutralization"],
                "truncation": sv["truncation"],
                "pasteurization": "ON",
                "testPeriod": "P0Y0M0D",
                "unitHandling": "VERIFY",
                "nanHandling": "OFF",
                "language": "FASTEXPR",
                "visualization": False,
            },
            "regular": formula,
            "dataset": dataset_name,
            "hypothesis": f"Systematic quantitatively-modeled signal for family '{bp.get('theme', 'Custom')}' using {f1} (Lookback={d} days)."
        }
        generated_configs.append(alpha_obj)

    log(f"Successfully generated {len(generated_configs)} unique WQ FastExpr alphas!")
    
    # Save generated alphas
    out_file = alpha_dataset_dir / "generated_alphas.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(generated_configs, f, indent=2)
    log(f"Step 4: Saved formulas portfolio -> alphas_dataset/{dataset_name}/alphas/generated_alphas.json")

    # 6. Push all alphas to the local review inbox
    log("Step 5: Injecting generated alphas to AlphaForge Review Inbox...")
    import requests
    
    push_url = f"http://{SERVER_HOST}:{SERVER_PORT}/api/queue-alpha"
    
    headers = {
        "Authorization": f"Bearer {active_token}",
        "Content-Type": "application/json"
    }
    
    # Format payload for push
    payload = []
    for a in generated_configs:
        payload.append({
            "formula": a["regular"],
            "family": f"{dataset_name}_gen",
            "hypothesis": a["hypothesis"],
            "settings": a["settings"]
        })
        
    try:
        log(f"Sending secure HTTP POST to console server review inbox at: {push_url}...")
        r = requests.post(push_url, json=payload, headers=headers, timeout=20)
        if r.status_code == 200:
            res = r.json()
            log(f"[SUCCESS] All {len(generated_configs)} alphas successfully pushed to console server review inbox!")
            log(f"          - Added count: {res.get('added', 0)}")
            log(f"          - Skipped count: {res.get('skipped', 0)}")
            log("Open your web console at http://127.0.0.1:8000 to backtest or submit these alphas!")
            return True, "Trigger flow completed successfully"
        else:
            log(f"[ERROR] API returned error status {r.status_code}: {r.text}", "WARNING")
            return False, f"Server returned error code {r.status_code}"
    except Exception as e:
        log(f"[ERROR] Failed to push to local console server: {e}", "WARNING")
        log("Check if your Flask dashboard is currently running on http://127.0.0.1:8000.")
        return True, "Generated alphas saved locally, but failed to push to running dashboard (not running?)"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AlphaForge - WQ Trigger Flow Executer")
    parser.add_argument("--dataset", type=str, default="analyst10", help="The target dataset search name (e.g. analyst10, fundamental8)")
    parser.add_argument("--count", type=int, default=200, help="How many alphas to generate")
    parser.add_argument("--token", type=str, default=None, help="Secure console Authorization Bearer token")
    parser.add_argument("--gemini_key", type=str, default=None, help="Gemini API Key override")
    
    args = parser.parse_args()
    
    success, msg = run_trigger_flow(args.dataset, args.count, args.token, args.gemini_key)
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

import sys
import json
import argparse
from src.auth import WQSession
from src.client import WQClient
from src.database import init_db, save_alpha_run, save_submitted_alpha
from src.validator import validate_fastexpr
from src.evaluator import evaluate_alpha_metrics
from src.logger import agent_logger

def run_single(formula: str, family: str, universe: str, neutralization: str, decay: int, region: str):
    init_db()

    # 1. Local Validation
    is_valid, err = validate_fastexpr(formula)
    if not is_valid:
        print(json.dumps({
            "status": "ERROR",
            "error_message": f"Local Validation Failed: {err}"
        }))
        return

    # 2. Login & Connect
    try:
        session = WQSession()
        client = WQClient(session)
    except Exception as e:
        print(json.dumps({
            "status": "ERROR",
            "error_message": f"Auth / Client initiation failed: {e}"
        }))
        return

    # 3. Simulate
    settings = {
        "universe": universe,
        "neutralization": neutralization,
        "decay": decay,
        "region": region
    }
    
    agent_logger.info(f"[CHAT AGENT] Simulating: {formula} | Universe={universe} | Neutralization={neutralization} | Decay={decay}")
    res = client.simulate_alpha(formula, settings)
    
    # 4. Evaluate
    status = evaluate_alpha_metrics(res)
    res["status"] = status

    # 5. Save to Database
    run_data = {
        "run_id": "chat-run",
        "family": family,
        "hypothesis": f"Chat generated alpha for {family} family",
        "formula": formula,
        "region": region,
        "universe": universe,
        "neutralization": neutralization,
        "decay": decay,
        "truncation": 0.1,
        "delay": 1,
        "sharpe": res.get("sharpe"),
        "fitness": res.get("fitness"),
        "turnover": res.get("turnover"),
        "checks_passed": res.get("checks_passed", 0),
        "weight_check": res.get("weight_check", "FAIL"),
        "sub_sharpe": res.get("sub_sharpe"),
        "status": status,
        "alpha_link": res.get("alpha_link"),
        "sim_link": res.get("sim_link"),
        "error_message": res.get("error_message"),
        "llm_model": "chat-copilot",
        "parent_id": None
    }
    row_id = save_alpha_run(run_data)

    # 6. Submit if submittable
    submission_details = None
    if status == "SUBMITTED":
        submit_res = client.submit_alpha(res["alpha_id"])
        submission_details = submit_res
        if submit_res["success"]:
            save_submitted_alpha(row_id, res["alpha_id"], self_corr_pass=True)
            res["status"] = "SUBMITTED_SUCCESS"
        else:
            res["status"] = "CORRELATED_FAIL"

    output = {
        "database_row_id": row_id,
        "metrics": res,
        "submission": submission_details
    }
    print(json.dumps(output))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run single alpha simulation via command line")
    parser.add_argument("--formula", required=True, help="Fast Expression formula")
    parser.add_argument("--family", default="Price Reversion", help="Alpha Family theme")
    parser.add_argument("--universe", default="TOP3000", help="TOP3000, TOP1000")
    parser.add_argument("--neutralization", default="SUBINDUSTRY", help="SUBINDUSTRY, MARKET")
    parser.add_argument("--decay", type=int, default=6, help="Decay smoothing value")
    parser.add_argument("--region", default="USA", help="USA, CHN")

    args = parser.parse_args()
    run_single(args.formula, args.family, args.universe, args.neutralization, args.decay, args.region)

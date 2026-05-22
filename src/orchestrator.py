import time
import uuid
import random
import sqlite3
from src.config import DEFAULT_SIM_SETTINGS, DB_PATH, ALPHAS_OUT_DIR, MAX_CONCURRENT_SIMS
from src.auth import WQSession
from src.client import WQClient
from src.database import init_db, save_alpha_run, save_submitted_alpha, get_stats_summary
from src.families import FAMILIES
from src.generator import AlphaGenerator
from src.validator import validate_fastexpr
from src.evaluator import evaluate_alpha_metrics
from src.logger import agent_logger, update_agent_status

class AlphaOrchestrator:
    def __init__(self):
        self.running = False
        self.session = None
        self.client = None
        self.generator = None

    def stop(self):
        self.running = False
        update_agent_status("AGENT STOPPING")

    def run_loop(self):
        self.running = True
        init_db()
        update_agent_status("AGENT LOGGING IN")

        # 1. Login & Establish session
        try:
            self.session = WQSession()
            self.client = WQClient(self.session)
            self.generator = AlphaGenerator()
            update_agent_status("AGENT RUNNING")
        except Exception as e:
            agent_logger.error(f"[SYSTEM] Startup failed: {e}")
            self.running = False
            update_agent_status("AGENT INACTIVE")
            return

        # 2. Main workflow loop
        from concurrent.futures import ThreadPoolExecutor

        while self.running:
            run_uuid = str(uuid.uuid4())[:8]
            agent_logger.info(f"\n--- [RUN {run_uuid}] Starting concurrent batch of {MAX_CONCURRENT_SIMS} research iterations ---")

            # Selection, Generation, and Validation Phase for Alphas
            batch_tasks = []
            for i in range(MAX_CONCURRENT_SIMS):
                if not self.running:
                    break
                family = self._select_family()
                formula, reasoning = self.generator.generate_alpha(family)
                agent_logger.info(f"[GENERATOR] [{i+1}/{MAX_CONCURRENT_SIMS}] Proposed Formula: {formula}")
                agent_logger.info(f"[GENERATOR] [{i+1}/{MAX_CONCURRENT_SIMS}] Hypothesis: {reasoning}")

                # Validation Phase
                is_valid, err = validate_fastexpr(formula)
                if not is_valid:
                    agent_logger.warning(f"[VALIDATOR] Local check failed: {err}")
                    # Save failed record to database
                    save_alpha_run({
                        "run_id": run_uuid, "family": family, "hypothesis": reasoning, "formula": formula,
                        "region": "USA", "universe": "TOP3000", "neutralization": "SUBINDUSTRY", "decay": 6,
                        "truncation": 0.1, "delay": 1, "sharpe": None, "fitness": None, "turnover": None,
                        "checks_passed": 0, "weight_check": "FAIL", "sub_sharpe": None, "status": "HARD_REJECT",
                        "alpha_link": None, "sim_link": None, "error_message": f"Syntax Check: {err}",
                        "llm_model": "gemini-1.5-flash", "parent_id": None
                    })
                    continue

                batch_tasks.append((family, reasoning, formula))

            # Run simulations concurrently for valid expressions
            if batch_tasks and self.running:
                agent_logger.info(f"[SYSTEM] Dispatching {len(batch_tasks)} simulations in parallel (max limit of {MAX_CONCURRENT_SIMS} concurrent)...")
                
                def _sim_task(item):
                    fam, reason, form = item
                    settings = dict(DEFAULT_SIM_SETTINGS)
                    try:
                        self._run_simulation_flow(run_uuid, fam, reason, form, settings)
                    except Exception as e:
                        agent_logger.error(f"[SYSTEM] Simulation batch thread error: {e}")

                with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_SIMS) as executor:
                    list(executor.map(_sim_task, batch_tasks))

            # Check if stopped early
            if not self.running:
                break

            # 180-second cooldown sleep as requested
            agent_logger.info("[SYSTEM] Cooldown period active. Sleeping for 180 seconds to prevent rate limits...")
            for _ in range(180):
                if not self.running:
                    break
                time.sleep(1)


        update_agent_status("AGENT INACTIVE")
        agent_logger.info("[SYSTEM] Orchestration loop stopped cleanly.")

    def _select_family(self) -> str:
        """
        Applies a selection algorithm:
        1. If any family has < 3 runs, pick the least-explored.
        2. 20% of the time, explore randomly.
        3. 80% of the time, pick the family with the highest success_rate.
        """
        families_list = list(FAMILIES.keys())
        try:
            stats = get_stats_summary()
            family_stats_map = {f["family"]: f for f in stats["families"]}
            
            # Check for under-explored families
            for f in families_list:
                run_count = family_stats_map.get(f, {}).get("total_runs", 0)
                if run_count < 3:
                    agent_logger.info(f"[STRATEGY] Theme '{f}' has < 3 runs. Prioritizing exploration.")
                    return f

            # 20% exploration
            if random.random() < 0.2:
                selected = random.choice(families_list)
                agent_logger.info(f"[STRATEGY] Random theme exploration: '{selected}'")
                return selected

            # 80% exploitation: sort by success rate
            sorted_families = sorted(
                families_list, 
                key=lambda f: family_stats_map.get(f, {}).get("success_rate", 0.0), 
                reverse=True
            )
            selected = sorted_families[0]
            agent_logger.info(f"[STRATEGY] Selecting highest success theme: '{selected}' ({family_stats_map.get(selected, {}).get('success_rate', 0.0)}% success)")
            return selected

        except Exception as e:
            agent_logger.warning(f"[STRATEGY] Error querying database statistics: {e}. Defaulting to random.")
            return random.choice(families_list)

    def _run_simulation_flow(self, run_id: str, family: str, hypothesis: str, formula: str, settings: dict, parent_id: int = None) -> int:
        """
        Runs simulation, evaluates metrics, saves to DB, submits if matching thresholds,
        and triggers setting adjustments (Soft Fail) recursively once.
        """
        # Call client simulation
        res = self.client.simulate_alpha(formula, settings)
        
        status = evaluate_alpha_metrics(res)
        
        run_data = {
            "run_id": run_id, "family": family, "hypothesis": hypothesis, "formula": formula,
            "region": settings.get("region", "USA"), "universe": settings.get("universe", "TOP3000"),
            "neutralization": settings.get("neutralization", "SUBINDUSTRY"), "decay": settings.get("decay", 6),
            "truncation": settings.get("truncation", 0.1), "delay": settings.get("delay", 1),
            "sharpe": res.get("sharpe"), "fitness": res.get("fitness"), "turnover": res.get("turnover"),
            "checks_passed": res.get("checks_passed", 0), "weight_check": res.get("weight_check", "FAIL"),
            "sub_sharpe": res.get("sub_sharpe"), "status": status, "alpha_link": res.get("alpha_link"),
            "sim_link": res.get("sim_link"), "error_message": res.get("error_message"),
            "llm_model": "gemini-1.5-flash", "parent_id": parent_id
        }

        # Save to DB
        row_id = save_alpha_run(run_data)

        # Save to alphas output directory if simulated successfully
        if status == "SUBMITTED" and res.get("alpha_id"):
            try:
                import json
                alpha_file = ALPHAS_OUT_DIR / f"alpha_{res['alpha_id']}.json"
                alpha_file.write_text(json.dumps({
                    "alpha_id": res["alpha_id"],
                    "formula": formula,
                    "family": family,
                    "hypothesis": hypothesis,
                    "status": status,
                    "sharpe": res.get("sharpe"),
                    "fitness": res.get("fitness"),
                    "turnover": res.get("turnover"),
                    "settings": settings,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }, indent=2), encoding="utf-8")
                agent_logger.info(f"[SYSTEM] Saved alpha details to file: {alpha_file}")
            except Exception as e:
                agent_logger.warning(f"[SYSTEM] Failed to write alpha file: {e}")


        # 1. Submission path
        if status == "SUBMITTED":
            submit_res = self.client.submit_alpha(res["alpha_id"])
            if submit_res["success"]:
                agent_logger.info(f"[SUBMISSION] Alpha successfully submitted! Link: {res['alpha_link']}")
                save_submitted_alpha(row_id, res["alpha_id"], self_corr_pass=True)
            else:
                agent_logger.warning(f"[SUBMISSION] Submission skipped/failed: {submit_res['details']}")
                # Update status to failed submission
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("UPDATE alpha_runs SET status = 'CORRELATED' WHERE id = ?", (row_id,))
                conn.commit()
                conn.close()

        # 2. Borderline / Soft Fail parameter tuning path
        elif status == "SOFT_FAIL" and parent_id is None:
            # We tune parameters and run a child variation simulation once
            new_settings = dict(settings)
            turnover = res.get("turnover", 0.0)
            
            # Smart tuning adjustment
            if turnover > 50.0:
                # High turnover: increase decay to smooth signals
                new_settings["decay"] = min(settings["decay"] + 4, 15)
                agent_logger.info(f"[TUNING] High turnover detected ({turnover:.1f}%). Increasing decay to {new_settings['decay']}.")
            elif turnover < 3.0:
                # Low turnover: decrease decay to make signal more responsive
                new_settings["decay"] = max(settings["decay"] - 2, 2)
                agent_logger.info(f"[TUNING] Low turnover detected ({turnover:.1f}%). Decreasing decay to {new_settings['decay']}.")
            else:
                # Change neutralization layer
                new_settings["neutralization"] = "MARKET" if settings["neutralization"] == "SUBINDUSTRY" else "SUBINDUSTRY"
                agent_logger.info(f"[TUNING] Adjusting neutralization to {new_settings['neutralization']} to look for different risk bounds.")

            agent_logger.info(f"[TUNING] Retrying formula with new settings config: {new_settings}")
            self._run_simulation_flow(run_id, family, hypothesis, formula, new_settings, parent_id=row_id)

        return row_id

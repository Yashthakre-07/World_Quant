import time
import threading
from src.auth import WQSession
from src.config import WQ_SIM_URL, WQ_ALPHAS_URL
from src.logger import agent_logger

_push_lock = threading.Lock()
_last_push_time = 0.0

class WQClient:
    def __init__(self, session: WQSession):
        self.session = session

    def simulate_alpha(self, formula: str, settings: dict) -> dict:
        """
        Submits an alpha formula to WorldQuant Brain for simulation.
        Polls until completion and returns the final metrics and checks.
        """
        payload = {
            "regular": formula.strip(),
            "type": "REGULAR",
            "settings": {
                "nanHandling": settings.get("nanHandling", "OFF"),
                "instrumentType": "EQUITY",
                "delay": settings.get("delay", 1),
                "universe": settings.get("universe", "TOP3000"),
                "truncation": settings.get("truncation", 0.1),
                "unitHandling": "VERIFY",
                "pasteurization": settings.get("pasteurization", "ON"),
                "region": settings.get("region", "USA"),
                "language": "FASTEXPR",
                "decay": settings.get("decay", 6),
                "neutralization": settings.get("neutralization", "SUBINDUSTRY"),
                "visualization": False
            }
        }

        # Short 1-second delay between concurrent submissions to prevent request collisions
        global _last_push_time
        with _push_lock:
            elapsed = time.time() - _last_push_time
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
            _last_push_time = time.time()

        agent_logger.info(f"[SIMULATION] Sending simulation request for formula: {formula}")
        
        try:
            r = self.session.post(WQ_SIM_URL, json=payload)
            if r.status_code not in [200, 201]:
                # If credentials expired, raise exception to trigger re-auth
                if r.status_code == 401:
                    self.session.login_expired = True
                    raise ValueError("Session expired or invalid credentials.")
                return {"status": "ERROR", "error_message": f"HTTP {r.status_code}: {r.text}"}

            if 'Location' not in r.headers:
                return {"status": "ERROR", "error_message": f"Location header missing: {r.text}"}

            nxt = r.headers['Location']
            agent_logger.info(f"[SIMULATION] Obtained simulation polling link: {nxt}")
        except Exception as e:
            agent_logger.error(f"[SIMULATION] Failed to submit: {e}")
            return {"status": "ERROR", "error_message": str(e)}

        # Poll the simulation progress
        retry_count = 0
        while True:
            try:
                poll_r = self.session.get(nxt)
                if poll_r.status_code != 200:
                    agent_logger.warning(f"[SIMULATION] Poll response code {poll_r.status_code}")
                    time.sleep(10)
                    continue

                res = poll_r.json()
                if 'alpha' in res:
                    alpha_id = res['alpha']
                    agent_logger.info(f"[SIMULATION] Simulation finished! Alpha ID: {alpha_id}")
                    break
                
                progress = int(res.get('progress', 0) * 100)
                agent_logger.info(f"[SIMULATION] Polling simulation progress... ({progress}%)")
                
                # Check for errors in the poll response
                if 'message' in res and 'error' in str(res.get('message', '')).lower():
                    return {
                        "status": "ERROR",
                        "error_message": res['message'],
                        "sim_link": nxt
                    }
            except Exception as e:
                agent_logger.error(f"[SIMULATION] Polling error: {e}")
                retry_count += 1
                if retry_count > 10:
                    return {"status": "ERROR", "error_message": f"Polling failed too many times: {e}"}
            
            time.sleep(60)



        # Retrieve final alpha metrics
        try:
            alpha_url = f"{WQ_ALPHAS_URL}/{alpha_id}"
            alpha_r = self.session.get(alpha_url).json()

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
                if check.get("name") == "LOW_SUB_UNIVERSE_SHARPE":
                    sub_sharpe = check.get("value", -1.0)

            return {
                "status": "SUCCESS",
                "alpha_id": alpha_id,
                "sharpe": sharpe,
                "fitness": fitness,
                "turnover": turnover,
                "checks_passed": checks_passed,
                "weight_check": weight_check,
                "sub_sharpe": sub_sharpe,
                "alpha_link": f"https://platform.worldquantbrain.com/alpha/{alpha_id}",
                "sim_link": nxt
            }
        except Exception as e:
            agent_logger.error(f"[SIMULATION] Error fetching alpha details: {e}")
            return {"status": "ERROR", "error_message": f"Fetch error: {e}", "alpha_id": alpha_id}

    def submit_alpha(self, alpha_id: str) -> dict:
        """
        Submits a passing alpha and checks self-correlation.
        """
        submit_url = f"{WQ_ALPHAS_URL}/{alpha_id}/submit"
        agent_logger.info(f"[SUBMISSION] Initiating submission for alpha {alpha_id}...")

        try:
            # POST to trigger submission
            r = self.session.post(submit_url, timeout=30)
            if r.status_code == 404:
                agent_logger.warning(f"[SUBMISSION] Alpha {alpha_id} already submitted (404 received).")
                return {"success": True, "details": "Already submitted"}

            # Poll GET to await result
            poll_limit = 50
            for poll_i in range(poll_limit):
                submit_r = self.session.get(submit_url, timeout=30)
                
                # 404 means checks completed successfully and alpha is submitted
                if submit_r.status_code == 404:
                    agent_logger.info(f"[SUBMISSION] Alpha {alpha_id} submitted successfully!")
                    return {"success": True, "details": "Success"}
                
                # 403 means submission checks failed (rejected)
                if submit_r.status_code == 403:
                    details = "Submission checks failed"
                    try:
                        res_json = submit_r.json()
                        checks = res_json.get("is", {}).get("checks", [])
                        failed = [c for c in checks if c.get("result") == "FAIL"]
                        if failed:
                            details = "; ".join([f"{c['name']}={c.get('value','')}" for c in failed])
                    except Exception:
                        details = submit_r.text[:200]
                    agent_logger.warning(f"[SUBMISSION] Alpha {alpha_id} rejected: {details}")
                    return {"success": False, "details": details}

                # If 200/201, parse checks and search for failures
                if submit_r.status_code in (200, 201) and submit_r.content:
                    try:
                        res_json = submit_r.json()
                        checks = res_json.get("is", {}).get("checks", [])
                        
                        # Check if any check has failed
                        failed = [c for c in checks if c.get("result") == "FAIL"]
                        if failed:
                            details = "; ".join([f"{c['name']}={c.get('value','')}" for c in failed])
                            agent_logger.warning(f"[SUBMISSION] Alpha {alpha_id} check failed: {details}")
                            return {"success": False, "details": details}
                    except Exception as json_err:
                        agent_logger.warning(f"[SUBMISSION] Error parsing JSON during polling: {json_err}")
                
                agent_logger.info(f"[SUBMISSION] Alpha {alpha_id}: checks in progress... (poll {poll_i+1}/{poll_limit})")
                time.sleep(10)
            
            return {"success": False, "details": "Polling timed out"}
        except Exception as e:
            agent_logger.error(f"[SUBMISSION] Failed submission request: {e}")
            return {"success": False, "details": str(e)}


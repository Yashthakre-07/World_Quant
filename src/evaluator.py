from src.config import (
    SHARPE_THRESHOLD_PASS, SHARPE_THRESHOLD_RETRY, FITNESS_THRESHOLD,
    MIN_TURNOVER, MAX_TURNOVER
)
from src.logger import agent_logger

def evaluate_alpha_metrics(results: dict) -> str:
    """
    Evaluates simulated alpha metrics and returns the quality status:
    'SUBMITTED', 'SOFT_FAIL', 'HARD_REJECT', or 'ERROR'.
    """
    if results.get("status") == "ERROR":
        return "ERROR"

    sharpe = results.get("sharpe")
    fitness = results.get("fitness")
    turnover = results.get("turnover", 0.0)
    weight_check = results.get("weight_check", "FAIL")

    # If metrics are missing due to early simulation crashes
    if sharpe is None or fitness is None:
        agent_logger.warning(f"[EVALUATOR] Missing metrics for alpha: Sharpe={sharpe}, Fitness={fitness}.")
        return "HARD_REJECT"

    # 1. Hard Rejects
    if sharpe < SHARPE_THRESHOLD_RETRY:
        reason = f"Sharpe {sharpe:.2f} is below minimum retry limit {SHARPE_THRESHOLD_RETRY}"
        agent_logger.info(f"[EVALUATOR] Classification: HARD_REJECT (Reason: {reason})")
        return "HARD_REJECT"

    if turnover < MIN_TURNOVER or turnover > MAX_TURNOVER:
        reason = f"Turnover {turnover:.1f}% is outside allowed bounds [{MIN_TURNOVER}%, {MAX_TURNOVER}%]"
        agent_logger.info(f"[EVALUATOR] Classification: HARD_REJECT (Reason: {reason})")
        return "HARD_REJECT"

    if weight_check == "FAIL":
        reason = "Weight concentration check failed (CONCENTRATED_WEIGHT = FAIL)"
        agent_logger.info(f"[EVALUATOR] Classification: HARD_REJECT (Reason: {reason})")
        return "HARD_REJECT"

    # 2. Soft Fails (Borderline metrics, good for adjusting neutralization/decay settings)
    if sharpe < SHARPE_THRESHOLD_PASS or fitness < FITNESS_THRESHOLD:
        reason = f"Sharpe={sharpe:.2f} (pass threshold: {SHARPE_THRESHOLD_PASS}) or Fitness={fitness:.2f} (pass threshold: {FITNESS_THRESHOLD}) is borderline."
        agent_logger.info(f"[EVALUATOR] Classification: SOFT_FAIL (Reason: {reason})")
        return "SOFT_FAIL"

    # 3. Success (Passes all criteria, submittable!)
    agent_logger.info(f"[EVALUATOR] Classification: SUBMITTABLE! Sharpe={sharpe:.2f}, Fitness={fitness:.2f}, Turnover={turnover:.1f}%")
    return "SUBMITTED"

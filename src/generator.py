import re
import random
import google.generativeai as genai
from src.config import GEMINI_API_KEY
from src.families import FAMILIES, OPERATORS_HELP
from src.database import get_learning_history
from src.logger import agent_logger

class AlphaGenerator:
    def __init__(self):
        self.api_enabled = False
        if GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.api_enabled = True
                agent_logger.info("[GENERATOR] Gemini API client successfully initialized.")
            except Exception as e:
                agent_logger.warning(f"[GENERATOR] Failed to configure Gemini API client: {e}. Running in seed fallback mode.")
        else:
            agent_logger.warning("[GENERATOR] GEMINI_API_KEY is not set in .env. Running in seed fallback mode.")

    def _generate_fallback(self, family_name: str) -> tuple[str, str]:
        """
        Fallback generator that takes seed formulas and applies parameter mutations.
        Allows testing the agent system without an active LLM key.
        """
        family_data = FAMILIES[family_name]
        seed = random.choice(family_data["seeds"])
        
        # Simple rule-based variations to create new expressions
        # E.g., replace digits (like lookbacks) with random lookbacks [5, 10, 20, 30, 60]
        lookbacks = [5, 10, 15, 20, 22, 30, 40, 60, 120]
        
        def replace_num(match):
            return str(random.choice(lookbacks))

        mutated = re.sub(r'\b\d+\b', replace_num, seed)
        
        # Ensure it has simple variations if no digits were matched
        if mutated == seed:
            mutated = f"rank({seed})"
            
        reasoning = f"Mutated variation of seed formula for {family_name} with lookback tuning."
        return mutated, reasoning

    def generate_alpha(self, family_name: str) -> tuple[str, str]:
        """
        Generates an alpha expression.
        Returns a tuple of (formula, reasoning).
        """
        if not self.api_enabled:
            return self._generate_fallback(family_name)

        family_data = FAMILIES[family_name]
        successes, failures = get_learning_history(family_name, limit=1)

        # Build prompt history
        success_str = "\n".join([f"- {s[0]} (Sharpe: {s[1]:.2f})" for s in successes])
        fail_str = "\n".join([f"- {f[0]}" for f in failures])

        if not success_str:
            success_str = "None."
        if not fail_str:
            fail_str = "None."

        seeds_str = "\n".join([f"- {seed}" for seed in family_data["seeds"]])

        allowed_fields = family_data.get("allowed_fields", ["open", "high", "low", "close", "vwap", "returns", "volume", "adv20", "cap"])
        allowed_fields_str = ", ".join(allowed_fields)

        prompt = f"""
Task: ONE alpha in WQ FastExpr.
Theme: {family_name}
Hypothesis: {family_data['hypothesis']}

Allowed Fields: {allowed_fields_str}
Core Ops: rank, zscore, scale, ts_delta, ts_delay, ts_decay_linear, group_neutralize, trade_when

RULES:
1. Bal brackets. No spaces. Output ONLY <formula>.
2. Test: "{family_data['hypothesis']}"
3. Avoid fails:
{fail_str}
4. WQ COMPLIANCE:
   - Wrap all analyst consensus/actual fields (starting with 'anl') in vec_avg(field) before mathematical, absolute, or time-series operators (e.g., ts_std_dev(vec_avg(field), N)).
   - Any standard deviation divisor MUST have a small non-zero offset added: (ts_std_dev(vec_avg(field), N) + 0.001) to prevent NaN/zero crashes.

Winners:
{success_str}

Seeds:
{seeds_str}

OUTPUT FORMAT (XML only):
<formula>formula</formula>
"""

        try:
            agent_logger.info(f"[GENERATOR] Requesting formula from Gemini API for family '{family_name}'...")
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Parsing xml-like tags
            formula_match = re.search(r'<formula>(.*?)</formula>', text, re.DOTALL)
            
            formula = formula_match.group(1).strip() if formula_match else ""
            reasoning = "Token-optimized gen."

            if not formula:
                # If extraction fails, try matching any non-xml line
                clean_lines = [line.strip() for line in text.split("\n") if not line.startswith("<")]
                if clean_lines:
                    formula = clean_lines[0]
            
            # Clean formula spacing
            formula = formula.replace("\n", "").replace(" ", "")
            # Ensure basic cleanup
            return formula, reasoning
            
        except Exception as e:
            agent_logger.error(f"[GENERATOR] Gemini API error: {e}. Falling back to rule-based seed mutation.")
            return self._generate_fallback(family_name)

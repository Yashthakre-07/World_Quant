import re
import json
from src.logger import agent_logger

import csv
from pathlib import Path

# Base price-volume fields
ALLOWED_FIELDS = {"open", "high", "low", "close", "vwap", "returns", "volume", "adv20", "cap"}

def load_custom_fields():
    custom = set()
    base_dir = Path(__file__).resolve().parent.parent
    
    # 1. Load from fields_index.csv
    csv_path = base_dir / "documentation" / "dataset" / "fields_index.csv"
    if csv_path.exists():
        try:
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # skip header
                for row in reader:
                    if len(row) >= 4:
                        field_id = row[3].strip()
                        if field_id:
                            custom.add(field_id)
        except Exception:
            pass
            
    # 2. Dynamically load from any JSON field registries in alphas_dataset/
    alphas_dataset_dir = base_dir / "alphas_dataset"
    if alphas_dataset_dir.exists():
        try:
            for p in alphas_dataset_dir.glob("**/fields.json"):
                with open(p, "r", encoding="utf-8") as f:
                    fields_data = json.load(f)
                    for item in fields_data:
                        if isinstance(item, dict) and "id" in item:
                            custom.add(item["id"])
        except Exception:
            pass
            
    return custom

ALLOWED_FIELDS.update(load_custom_fields())

# List of allowed operators
ALLOWED_OPS = {
    # Cross sectional
    "rank", "zscore", "scale", "sigmoid", "exp", "fraction", "log", "log_diff", "pasteurize", "abs", "sign", "signed_power", "max", "min",
    # Time series
    "ts_delta", "ts_delay", "ts_rank", "ts_sum", "ts_mean", "ts_std_dev", "ts_corr", "ts_covariance", "ts_regression", 
    "ts_decay_linear", "ts_product", "ts_max", "ts_min", "ts_arg_max", "ts_arg_min", "ts_max_diff", "ts_min_diff", 
    "ts_av_diff", "ts_ir", "ts_skewness", "ts_kurtosis", "ts_entropy", "ts_median",
    # Group operators
    "group_neutralize", "group_zscore", "group_rank", "group_mean", "group_std_dev", "group_sum", "group_scale", 
    "group_max", "group_median",
    # Groups
    "market", "sector", "industry", "subindustry",
    # Conditional
    "trade_when"
}

def validate_fastexpr(formula: str) -> tuple[bool, str]:
    """
    Validates a Fast Expression formula locally.
    Returns (is_valid, error_message).
    """
    expr = formula.strip()
    if not expr:
        return False, "Formula is empty."

    # Compiler Safety: absolute value operator is prohibited
    expr_clean = expr.replace(" ", "").lower()
    if "abs(" in expr_clean:
        return False, "BANNED OPERATOR: 'abs()' is prohibited."

    # Compiler Safety: Banned smoothing on event fields
    illegal_smoothers = ("ts_decay_linear", "ts_mean", "ts_std_dev", "ts_sum")
    for smoother in illegal_smoothers:
        pattern = rf"{smoother}\([^)]*anl"
        if re.search(pattern, expr_clean):
            return False, f"COMPILER VIOLATION: Cannot smooth event fields using '{smoother}'."

    # 1. Bracket Matching Check
    stack = []
    brackets = {"(": ")", "[": "]", "{": "}"}
    for char in expr:
        if char in brackets.keys():
            stack.append(char)
        elif char in brackets.values():
            if not stack:
                return False, "Unbalanced closing bracket."
            last = stack.pop()
            if brackets[last] != char:
                return False, f"Mismatched brackets: {last} and {char}."
    if stack:
        return False, f"Unbalanced opening brackets: {', '.join(stack)}."

    # 2. Token Validation (Operators & Fields)
    # Extract words using regex
    words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', expr)
    for word in words:
        # If it's a number, skip
        if word.isdigit():
            continue
        # If it is inside allowed fields or operators, skip
        if word in ALLOWED_FIELDS or word in ALLOWED_OPS:
            continue
        # Allow Analyst 10, 14, and 15 fields dynamically
        if word.startswith("anl10_") or word.startswith("anl14_") or word.startswith("anl15_") or word.startswith("anl4_"):
            continue
        # Some words could be noise or Python leaks
        return False, f"Illegal token found: '{word}'. Not in allowed data fields or operator list."

    # 3. Check for Python comparisons leak (like 'and', 'or', 'not' instead of '&&', '||', '!')
    if re.search(r'\b(and|or|not)\b', expr, re.IGNORECASE):
        return False, "Use logical operators '&&', '||', '!' instead of python words 'and', 'or', 'not'."

    # 4. Check for invalid consecutive/adjacent operators (like ++, --, **, //, ++*, *+, etc.)
    # Spaceless string helps check for cases with extra whitespace (e.g., '+ + *')
    spaceless_expr = re.sub(r'\s+', '', expr)
    if re.search(r'\+\++|\-\-+|\*\*|\/\/|%%|&&&|\|\|\|', spaceless_expr):
        return False, "Invalid consecutive operators detected (like ++, --, **, or //)."
    if re.search(r'\+\*|\*\+|\/\*|\*\/|\/\+|\+\/|\-\/', spaceless_expr):
        return False, "Invalid operator combination detected (like +*, *+, /*, */, /+, +/, or -/)."

    return True, "Valid syntax."

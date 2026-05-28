"""
STEP 1: Fetch analyst10 fields + all operators using ace_lib.
Run this script once while online to save fields locally.
Then run generate_analyst10_alphas.py to create the 200 alphas.

Usage:
    python fetch_analyst10_fields.py
"""

import json
import os
import sys

# Add ace_api_extracted folder to path so we can import ace_lib
ACE_LIB_DIR = r"C:\Users\Admin\Documents\VIBE_YT\wq\documentation\ace_api_extracted"
sys.path.insert(0, ACE_LIB_DIR)

import ace_lib

# --- Output folder ---
OUT_DIR = r"C:\Users\Admin\Documents\VIBE_YT\wq\alphas\analyst\analyst10"
os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("Connecting to WorldQuant BRAIN via ace_lib...")
s = ace_lib.start_session()
print("Session started.")

# ----------------------------------------------------------------
# 1. Fetch all operators
# ----------------------------------------------------------------
print("\n[1/3] Fetching all operators...")
operators_df = ace_lib.get_operators(s)
print(f"  Got {len(operators_df)} operator rows")
print(operators_df[["name", "syntax", "category"]].drop_duplicates("name").to_string())

# Save operators
operators_path = os.path.join(OUT_DIR, "operators.json")
ops_unique = operators_df.drop_duplicates("name")
with open(operators_path, "w", encoding="utf-8") as f:
    json.dump(ops_unique.to_dict("records"), f, indent=2)
print(f"  Saved operators -> {operators_path}")

# ----------------------------------------------------------------
# 2. Fetch datafields for analyst10  (USA, TOP3000, delay=1)
# ----------------------------------------------------------------
print("\n[2/3] Fetching analyst10 datafields (USA / TOP3000 / delay=1)...")
fields_df = ace_lib.get_datafields(
    s,
    instrument_type="EQUITY",
    region="USA",
    delay=1,
    universe="TOP3000",
    search="analyst10",
)
print(f"  Got {len(fields_df)} fields")
print(fields_df[["id", "description"]].head(40).to_string())

# Save fields
fields_path = os.path.join(OUT_DIR, "analyst10_fields.json")
with open(fields_path, "w", encoding="utf-8") as f:
    json.dump(fields_df.to_dict("records"), f, indent=2)
print(f"\n  Saved {len(fields_df)} fields -> {fields_path}")

# ----------------------------------------------------------------
# 3. Print unique field IDs so we can use them to write alphas
# ----------------------------------------------------------------
print("\n[3/3] Unique field IDs:")
for fid in sorted(fields_df["id"].unique()):
    desc = fields_df[fields_df["id"] == fid]["description"].iloc[0] if "description" in fields_df.columns else ""
    print(f"  {fid:60s} {str(desc)[:60]}")

print("\nDONE. Now use generate_analyst10_alphas.py to create the 200 alphas.")

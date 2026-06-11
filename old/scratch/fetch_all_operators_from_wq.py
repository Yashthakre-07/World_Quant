import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.auth import WQSession
import json

print("Initializing session for saineela731@gmail.com...")
# Let's override WQ_EMAIL and WQ_PASSWORD in src.config to make sure it loads correctly
import src.config
src.config.WQ_EMAIL = "saineela731@gmail.com"
src.config.WQ_PASSWORD = "iitg@123"

# Initialize session
session = WQSession(interactive=False, cli_mode=False)

print("Fetching operators...")
try:
    response = session.get("https://api.worldquantbrain.com/operators")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        ops = response.json()
        output_path = Path(__file__).resolve().parent / "wq_operators.json"
        with open(output_path, "w") as f:
            json.dump(ops, f, indent=2)
        print(f"Successfully fetched {len(ops.get('results', []))} / {len(ops)} operators. Saved to {output_path}")
    else:
        print(f"Failed: {response.text}")
except Exception as e:
    print(f"Error fetching operators: {e}")

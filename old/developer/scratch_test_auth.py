import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load sai.env
env_path = Path("sai.env")
if env_path.exists():
    load_dotenv(env_path, override=True)
else:
    load_dotenv()

from src.auth import WQSession

try:
    print(f"Testing login for: {os.getenv('WQ_EMAIL')}")
    session = WQSession()
    
    # Query users/self
    r = session.get("https://api.worldquantbrain.com/users/self")
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        print("User Self Data:")
        print(json.dumps(r.json(), indent=2))
    else:
        print(f"Error Response: {r.text}")
        
except Exception as e:
    print(f"Exception: {e}")

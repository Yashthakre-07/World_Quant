import json
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load sai.env
load_dotenv("sai.env", override=True)

from src.auth import WQSession

session = WQSession()

endpoints = [
    "users/self",
    "users/self/limits",
    "users/self/permissions",
    "users/self/status",
    "users/self/tier",
    "users/self/profile",
    "users/self/history",
    "users/self/metrics",
    "users/self/campaigns"
]

for ep in endpoints:
    url = f"https://api.worldquantbrain.com/{ep}"
    r = session.get(url)
    print(f"\n--- GET {url} ---")
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        try:
            print(json.dumps(r.json(), indent=2))
        except:
            print(r.text[:300])
    else:
        print(r.text[:200])

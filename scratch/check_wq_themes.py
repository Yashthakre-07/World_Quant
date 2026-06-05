import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.auth import WQSession
import json

print("Initializing session for saineela731@gmail.com...")
# Ensure credentials are set correctly
import src.config
src.config.WQ_EMAIL = "saineela731@gmail.com"
src.config.WQ_PASSWORD = "iitg@123"

session = WQSession(interactive=False, cli_mode=False)

print("\n--- Checking Active Themes / Thematic Datasets ---")

try:
    # 1. Check datasets with theme=true filter
    url_datasets = (
        "https://api.worldquantbrain.com/data-sets"
        "?instrumentType=EQUITY&region=USA&delay=1&universe=TOP3000&theme=true&limit=20"
    )
    r_ds = session.get(url_datasets, timeout=20)
    print(f"Datasets status: {r_ds.status_code}")
    if r_ds.status_code == 200:
        data = r_ds.json()
        results = data.get("results", [])
        print(f"Total thematic datasets: {data.get('count', 0)}")
        for ds in results[:10]:
            print(f"  * {ds.get('id')}: {ds.get('name')} | Category: {ds.get('category')} | Theme: {ds.get('theme', {}).get('name', 'N/A')}")
    else:
        print(f"Failed: {r_ds.text[:300]}")

    # 2. Check direct /themes or /campaigns endpoints if they exist
    endpoints = [
        "https://api.worldquantbrain.com/themes",
        "https://api.worldquantbrain.com/campaigns"
    ]
    for url in endpoints:
        print(f"\nChecking endpoint: {url} ...")
        r = session.get(url, timeout=20)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            res = r.json()
            if isinstance(res, dict):
                results = res.get("results", [])
                print(f"Count: {res.get('count', len(results))}")
                for item in results[:5]:
                    print(f"  * {item}")
            else:
                print(f"Response: {str(res)[:300]}")
        else:
            print(f"Failed: {r.text[:300]}")

except Exception as e:
    print(f"Error checking themes: {e}")

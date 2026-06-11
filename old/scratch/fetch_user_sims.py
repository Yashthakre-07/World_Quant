import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.auth import WQSession

def main():
    session = WQSession(email="saineela731@gmail.com", password="iitg@123")
    try:
        session.load_persisted_cookies()
    except Exception as e:
        print(f"Failed to load cookies: {e}")
        return

    url = "https://api.worldquantbrain.com/simulations"
    # Filter by user
    params = {"limit": 15}
    try:
        r = session.get(url, params=params, timeout=15)
        if r.status_code == 200:
            res = r.json()
            print("==========================================")
            print("RECENT SIMULATIONS ON WQ BRAIN:")
            print("==========================================")
            results = res.get("results", [])
            for i, sim in enumerate(results):
                sim_id = sim.get("id")
                status = sim.get("status")
                progress = sim.get("progress")
                created = sim.get("created")
                # Get formula snippet if single, or label
                code = sim.get("regular", {}).get("code", "Batch/Multi")
                print(f"[{i+1}] ID: {sim_id} | Status: {status} | Progress: {progress * 100 if progress else 0}% | Created: {created}")
                print(f"    Code: {code[:80]}...")
            print("==========================================")
        else:
            print(f"HTTP Error {r.status_code}: {r.text[:150]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

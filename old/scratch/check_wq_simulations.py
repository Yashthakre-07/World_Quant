import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.auth import WQSession

def check_sim(session, sim_id, label):
    url = f"https://api.worldquantbrain.com/simulations/{sim_id}"
    try:
        r = session.get(url, timeout=15)
        if r.status_code == 200:
            res = r.json()
            status = res.get("status")
            progress = res.get("progress")
            children = res.get("children", [])
            print(f"{label}: Status={status} | Progress={progress * 100 if progress else 0}% | Children={len(children)}")
            if children:
                print(f"  Child IDs: {', '.join(children[:4])}...")
        else:
            print(f"{label}: HTTP Error {r.status_code}: {r.text[:150]}")
    except Exception as e:
        print(f"{label}: Error: {e}")

def main():
    # Load session
    session = WQSession(email="saineela731@gmail.com", password="iitg@123")
    try:
        session.load_persisted_cookies()
    except Exception as e:
        print(f"Failed to load cookies: {e}")
        return

    sims = [
        ("Slot 1 (Alphas 1-4)", "z1sp7cYg5cab7RkTp4iDZR"),
        ("Slot 2 (Alphas 5-8)", "1J5ii8c95iicBx5zJOyp6j"),
        ("Slot 4 (Alphas 13-16)", "26woBs5wX4nvbGuey1UVzTh")
    ]
    
    # Get Slot 3 link if possible from log
    log_path = "C:/Users/Admin/.gemini/antigravity/brain/749bd3d6-c1f0-40b3-bfdc-5cc49cd235de/.system_generated/tasks/task-6437.log"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if "[Slot 3]" in line and "queued successfully" in line:
                    parts = line.split("Parent Link: ")
                    if len(parts) > 1:
                        sim_id = parts[1].split("/")[-1].strip()
                        if ("Slot 3 (Alphas 9-12)", sim_id) not in sims:
                            sims.insert(2, ("Slot 3 (Alphas 9-12)", sim_id))
    
    print("==========================================")
    print("LIVE SIMULATION STATUS DIRECT FROM WQ BRAIN:")
    print("==========================================")
    for label, sim_id in sims:
        check_sim(session, sim_id, label)
    print("==========================================")

if __name__ == "__main__":
    main()

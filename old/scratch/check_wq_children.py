import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.auth import WQSession

def check_child(session, child_id):
    url = f"https://api.worldquantbrain.com/simulations/{child_id}"
    try:
        r = session.get(url, timeout=15)
        if r.status_code == 200:
            res = r.json()
            status = res.get("status")
            progress = res.get("progress")
            # If complete, get metrics
            alpha_id = res.get("alpha")
            if alpha_id:
                # Get alpha details
                alpha_url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
                alpha_r = session.get(alpha_url, timeout=15)
                if alpha_r.status_code == 200:
                    alpha_res = alpha_r.json()
                    status = alpha_res.get("status")
                    is_metrics = alpha_res.get("is", {})
                    sharpe = is_metrics.get("sharpe")
                    fitness = is_metrics.get("fitness")
                    turnover = is_metrics.get("turnover", 0.0) * 100.0 if is_metrics.get("turnover") is not None else 0.0
                    code = alpha_res.get("regular", {}).get("code", "")
                    print(f"Child {child_id}: ALPHA STATUS={status} | Sharpe={sharpe} | Fitness={fitness} | Turnover={turnover:.1f}%")
                    print(f"  Formula: {code[:100]}...")
                else:
                    print(f"Child {child_id}: WQ Alpha status={status} (Alpha details HTTP {alpha_r.status_code})")
            else:
                # Not completed, show sim details
                error = res.get("error", {}).get("message") or res.get("message")
                print(f"Child {child_id}: SIM STATUS={status} | Progress={progress * 100 if progress else 0}% | Error={error}")
        else:
            print(f"Child {child_id}: HTTP Error {r.status_code}")
    except Exception as e:
        print(f"Child {child_id}: Error: {e}")

def main():
    session = WQSession(email="saineela731@gmail.com", password="iitg@123")
    try:
        session.load_persisted_cookies()
    except Exception as e:
        print(f"Failed to load cookies: {e}")
        return

    children = [
        # Slot 1
        "4zkO1s54j5bXchq4Hgvxkcs",
        "3jrkaN3PS4JR8x8LnGOTupQ",
        "4bDiF75zV50UbKRxG7FDwrj",
        "1czWoe6Ij4KJc5VHuTffFMp",
        # Slot 4
        "23xVEucO54qxbuAj5st30Bq",
        "2JJZJY3iK5dsc7y14Q6EUSwH",
        "1bZ2XoXx4su9EDvnyASa6Q",
        "3NQ0pi6Dx4xXcFjAWMBkHaM"
    ]
    
    print("==========================================")
    print("CHILD SIMULATION RESULTS DIRECT FROM WQ BRAIN:")
    print("==========================================")
    for cid in children:
        check_child(session, cid)
    print("==========================================")

if __name__ == "__main__":
    main()

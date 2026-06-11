import sys
import os
import json
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.auth import WQSession

def check_parent(session, parent_id):
    url = f"https://api.worldquantbrain.com/simulations/{parent_id}"
    try:
        r = session.get(url, timeout=15)
        if r.status_code == 200:
            res = r.json()
            status = res.get("status")
            progress = res.get("progress")
            print(f"\nParent {parent_id}: STATUS={status} | Progress={progress * 100 if progress is not None else 0}%")
            
            # Print children if they exist
            children = res.get("children", [])
            print(f"Found {len(children)} child simulations:")
            for child in children:
                child_id = child.get("id")
                # Fetch child details
                curl = f"https://api.worldquantbrain.com/simulations/{child_id}"
                cr = session.get(curl, timeout=10)
                if cr.status_code == 200:
                    cdata = cr.json()
                    cstatus = cdata.get("status")
                    cprogress = cdata.get("progress")
                    cerror = cdata.get("error", {}).get("message")
                    alpha_id = cdata.get("alpha")
                    
                    if alpha_id:
                        # Fetch alpha details
                        aurl = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
                        ar = session.get(aurl, timeout=10)
                        if ar.status_code == 200:
                            adata = ar.json()
                            astatus = adata.get("status")
                            metrics = adata.get("is", {})
                            asharpe = metrics.get("sharpe")
                            afit = metrics.get("fitness")
                            code = adata.get("regular", {}).get("code", "")
                            print(f"  - Child {child_id}: ALPHA STATUS={astatus} | Sharpe={asharpe} | Fitness={afit} | Formula={code[:80]}...")
                        else:
                            print(f"  - Child {child_id}: WQ Alpha status (Alpha details HTTP {ar.status_code})")
                    else:
                        print(f"  - Child {child_id}: SIM STATUS={cstatus} | Progress={cprogress * 100 if cprogress is not None else 0}% | Error={cerror}")
                else:
                    print(f"  - Child {child_id}: HTTP Error {cr.status_code}")
        else:
            print(f"\nParent {parent_id}: HTTP Error {r.status_code}")
    except Exception as e:
        print(f"\nParent {parent_id}: Error: {e}")

def main():
    session = WQSession(email="saineela731@gmail.com", password="iitg@123")
    try:
        session.load_persisted_cookies()
    except Exception as e:
        print(f"Failed to load cookies: {e}")
        return

    # Yash's running parent simulations from the log
    parents = [
        "18GHFK7qx55a9H6lBnEu990",  # Slot 2 (Alphas 5-8)
        "4tHj3idp055nbluZocUTYVl"   # Slot 1 (Alphas 1-4)
    ]
    
    print("==========================================")
    print("PARENT SIMULATION STATUS DIRECT FROM WQ:")
    print("==========================================")
    for pid in parents:
        check_parent(session, pid)
    print("==========================================")

if __name__ == "__main__":
    main()

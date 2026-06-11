import json
import os
import sys

def print_table():
    sys.stdout.reconfigure(encoding='utf-8')
    path = "scratch/generation_state.json"
    if not os.path.exists(path):
        print("generation_state.json not found!")
        return
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    history = data.get("history", [])
    
    print(f"{'Gen':<5}{'Sub':<5}{'Soft':<6}{'Hard':<6}{'Err':<5}{'Best Sharpe':<13}{'Time'}")
    print("-" * 65)
    for h in history:
        gen = h.get("generation_number")
        summary = h.get("summary", {})
        sub = summary.get("submitted", 0)
        soft = summary.get("soft_fail", 0)
        hard = summary.get("hard_reject", 0)
        err = summary.get("error", 0)
        best = summary.get("best_sharpe", 0.0)
        ts = h.get("timestamp", "").split("T")[0]
        
        print(f"{gen:<5}{sub:<5}{soft:<6}{hard:<6}{err:<5}{best:<13.4f}{ts}")

if __name__ == "__main__":
    print_table()

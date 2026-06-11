import json
import urllib.request
import urllib.error
import sys
from datetime import datetime

def run_step_0():
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Read group from pipeline state
    group = "groupa"
    try:
        with open("scratch/pipeline_state.json", "r", encoding="utf-8") as f:
            p_state = json.load(f)
            group = p_state.get("group", "groupa").lower()
    except Exception:
        pass

    # Read target generation
    try:
        with open("scratch/generation_state.json", "r", encoding="utf-8") as f:
            gen_state = json.load(f)
            target_gen = gen_state.get("current_generation", "N/A")
    except Exception:
        target_gen = "N/A"
        
    print(f"=== PIPELINE STEP 0: INITIATING CYCLE FOR GENERATION {target_gen} ({group.upper()}) ===")
    
    # Set token and slots based on group
    if group == "groupb":
        token = "yashthakrepro"
        target_slots = {5, 6, 7, 8}
    else:
        token = "yashthakreop"
        target_slots = {1, 2, 3, 4}

    url = "http://127.0.0.1:8000/api/status"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        print(f"Error connecting to server: {e}")
        return
        
    alphas = data.get("alphas", [])
    filtered_alphas = [a for a in alphas if a.get("slot_id") in target_slots]
    
    # Generate the Markdown report
    timestamp = datetime.now().isoformat()
    report = f"### 📊 Slot Status Report (Targeted Slots 1-4 for Generation {target_gen})\n"
    report += f"**Timestamp**: {timestamp}\n"
    report += f"**Target Server**: {url}\n"
    report += f"**Total Target Alphas**: {len(filtered_alphas)}\n\n"
    
    report += "| Slot ID | Status | Progress | Sharpe | Fitness | Turnover | Formula |\n"
    report += "|---|---|---|---|---|---|---|\n"
    
    for a in filtered_alphas:
        slot = a.get("slot_id", "N/A")
        status = a.get("status", "N/A")
        progress = a.get("progress", 0)
        sharpe = a.get("sharpe", "N/A")
        fitness = a.get("fitness", "N/A")
        turnover = a.get("turnover", "N/A")
        formula = a.get("formula", "")
        report += f"| {slot} | {status} | {progress}% | {sharpe} | {fitness} | {turnover} | `{formula}` |\n"
        
    with open("scratch/slot_status_report.md", "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"✅ Step 0 execution complete. Report written to scratch/slot_status_report.md (Target Generation: {target_gen})")

if __name__ == "__main__":
    run_step_0()

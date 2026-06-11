import json

log_path = r"C:\Users\Admin\.gemini\antigravity\brain\49144093-d93f-4680-a266-15768a9deb57\.system_generated\logs\transcript.jsonl"

targets = [2407, 2408, 2425, 2524, 2525]
with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            step_idx = data.get("step_index")
            if step_idx in targets:
                print(f"\n==================================")
                print(f"STEP {step_idx} | Source: {data.get('source')} | Type: {data.get('type')}")
                print(f"==================================")
                print(data.get("content"))
        except Exception:
            pass





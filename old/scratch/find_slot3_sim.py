import os
import re

log_path = "C:/Users/Admin/.gemini/antigravity/brain/749bd3d6-c1f0-40b3-bfdc-5cc49cd235de/.system_generated/tasks/task-6437.log"
if os.path.exists(log_path):
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    print(f"Total lines: {len(lines)}")
    for line in lines:
        if "queued successfully" in line or "Slot 3" in line or "Batch" in line:
            print(line.strip())
else:
    print("Log file not found.")

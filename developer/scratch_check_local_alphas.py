import os
from pathlib import Path
import json

local_dir = Path("alphas")
files = list(local_dir.glob("alpha_*.json"))
print("Total local files:", len(files))

# Let's count status
status_counts = {}
for f in files:
    try:
        with open(f, "r") as fh:
            data = json.load(fh)
            status = data.get("status")
            status_counts[status] = status_counts.get(status, 0) + 1
    except Exception as e:
        pass
print("Status breakdown:", status_counts)

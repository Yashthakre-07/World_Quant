import os
import sys

# Reconfigure stdout to use utf-8 to avoid encoding errors
sys.stdout.reconfigure(encoding='utf-8')

log_files = [
    "scratch/aql_run_log.txt",
    "scratch/run_log.txt",
    "scratch/dual_pipeline_run_log.txt",
]

search_terms = ["GRP_B_GEN11", "opipro", "groupb_generation", "overwrite-queue", "review-box", "review box"]

for file in log_files:
    if os.path.exists(file):
        print(f"\n================ SEARCHING IN: {file} ================")
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            for idx, line in enumerate(lines):
                for term in search_terms:
                    if term.lower() in line.lower():
                        # print surrounding context
                        start = max(0, idx - 4)
                        end = min(len(lines), idx + 5)
                        print(f"--- Line {idx} match '{term}': ---")
                        for i in range(start, end):
                            # safe print
                            clean_line = lines[i].strip().encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                            print(f"{i}: {clean_line}")
                        print()
                        break

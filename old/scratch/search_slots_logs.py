import os

log_files = [
    "live_run.txt",
    "scratch/run_log.txt",
    "scratch/opi_run_log.txt",
    "scratch/opipro_run_log.txt",
    "scratch/deep_status_output.txt"
]

search_terms = ["slot 5", "slot 6", "slot 7", "slots 5", "slots 6", "slots 7", "Slot: 5", "Slot: 6", "Slot: 7"]

for file in log_files:
    if os.path.exists(file):
        print(f"\n================ SEARCHING IN: {file} ================")
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            for idx, line in enumerate(lines):
                for term in search_terms:
                    if term.lower() in line.lower():
                        # print surrounding context
                        start = max(0, idx - 2)
                        end = min(len(lines), idx + 3)
                        print(f"--- Line {idx} match '{term}': ---")
                        for i in range(start, end):
                            print(f"{i}: {lines[i].strip()}")
                        print()
                        break

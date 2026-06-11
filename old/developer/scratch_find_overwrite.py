with open("run_pipeline.py", "r", encoding="utf-8", errors="ignore") as f:
    for idx, line in enumerate(f, 1):
        if "overwrite-queue" in line:
            print(f"Line {idx}: {line.strip()}")

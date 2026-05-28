import sys
with open("static/app.js", "r", encoding="utf-8", errors="ignore") as f:
    for idx, line in enumerate(f, 1):
        if "queue-status" in line or "status" in line or "/api/" in line:
            sys.stdout.buffer.write(f"Line {idx}: {line.strip()}\n".encode('utf-8'))

import re
content = open("run_pipeline.py", encoding="utf-8", errors="ignore").read()
routes = re.findall(r"app\.route\([\"'](/api/[^\"']+)", content)
for r in routes:
    print(r)

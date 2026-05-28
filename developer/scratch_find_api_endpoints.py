import re

with open("run_pipeline.py", "r", encoding="utf-8") as f:
    content = f.read()

matches = re.findall(r"@app\.route\([^)]+\)", content)
print("Found endpoints:")
for m in matches:
    print(m)

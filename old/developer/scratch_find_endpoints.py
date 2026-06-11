import re
with open('run_pipeline.py', 'r', encoding='utf-8') as f:
    text = f.read()
matches = re.findall(r'@app\.route\([\s\'\"]+([^\\\'\"]+)[\s\'\"]+', text)
print("Endpoints found:", matches)

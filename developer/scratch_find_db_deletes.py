import re

with open("run_pipeline.py", "r", encoding="utf-8") as f:
    content = f.read()

# Let's search for "DELETE" or "DROP" or "REMOVE"
deletes = re.findall(r"(?i)delete\s+from|drop\s+table|truncate", content)
print("Found deletion queries in run_pipeline.py:", deletes)

# Let's search for any endpoints that modify the DB in run_pipeline.py
matches = re.finditer(r"@app\.route\(\"([^\"]+)\"", content)
for m in matches:
    route = m.group(1)
    # Get the code for this route function
    # Let's print the route path
    print("Route:", route)

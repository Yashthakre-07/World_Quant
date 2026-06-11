import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

with urllib.request.urlopen('http://localhost:8000/api/status', timeout=10) as r:
    data = json.loads(r.read().decode('utf-8', errors='replace'))

alphas = data.get('alphas', [])

from collections import Counter
statuses = Counter(a.get('status','?') for a in alphas)
print(f"TOTAL ALPHAS IN QUEUE: {len(alphas)}")
print(f"STATUS BREAKDOWN: {dict(statuses)}")
print()

errors = [a for a in alphas if a.get('status') == 'ERROR']
print(f"ERROR ALPHAS: {len(errors)}")
print()

for a in errors:
    family  = a.get('family', '?')
    formula = a.get('formula', '')[:90]
    errmsg  = a.get('error_message') or 'NO ERROR MESSAGE STORED'
    print(f"FAMILY  : {family}")
    print(f"FORMULA : {formula}...")
    print(f"ERROR   : {errmsg}")
    print("-" * 70)

import requests
import json
import os

# Credentials
yash_env_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\yash.env"
email, password = None, None
with open(yash_env_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            if k.strip() == 'WQ_EMAIL': email = v.strip()
            elif k.strip() == 'WQ_PASSWORD': password = v.strip()

s = requests.Session()
s.auth = (email, password)
s.post("https://api.worldquantbrain.com/authentication")

# Try to query fields for analyst16 with different params
dataset_id = "analyst16"

print("--- Query with region=USA, delay=1, universe=TOP3000 ---")
url1 = f"https://api.worldquantbrain.com/data-fields?dataset.id={dataset_id}&instrumentType=EQUITY&region=USA&delay=1&universe=TOP3000&limit=10"
r = s.get(url1)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print(f"Count: {r.json().get('count')}")
    print(f"Results length: {len(r.json().get('results', []))}")

print("--- Query with no region/delay/universe filters ---")
url2 = f"https://api.worldquantbrain.com/data-fields?dataset.id={dataset_id}&limit=10"
r = s.get(url2)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print(f"Count: {r.json().get('count')}")
    print(f"Results length: {len(r.json().get('results', []))}")
    if r.json().get('results'):
        print("Sample field:")
        print(r.json().get('results')[0])

import requests
import json
import os

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

# Check dataset metadata from API directly
url = "https://api.worldquantbrain.com/data-sets/analyst16"
r = s.get(url)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2))
else:
    print(r.text)

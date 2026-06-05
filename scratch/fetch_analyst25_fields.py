import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.auth import WQSession
import json
import time

print("Initializing session...")
session = WQSession(interactive=False, cli_mode=False)

print("Fetching analyst25 datafields...")
all_fields = []
offset = 0
limit = 50
total = None

try:
    while True:
        url = (
            f"https://api.worldquantbrain.com/data-fields"
            f"?instrumentType=EQUITY"
            f"&region=USA"
            f"&delay=1"
            f"&universe=TOP3000"
            f"&dataset.id=analyst25"
            f"&limit={limit}"
            f"&offset={offset}"
        )
        r = session.get(url, timeout=20)
        if r.status_code == 429:
            print("Rate limited, sleeping 5s...")
            time.sleep(5)
            continue
        if r.status_code != 200:
            print(f"Failed to fetch fields: {r.status_code} {r.text}")
            break
        
        data = r.json()
        results = data.get("results", [])
        if total is None:
            total = data.get("count", 0)
            print(f"Total fields available: {total}")
            
        if not results:
            break
            
        all_fields.extend(results)
        offset += len(results)
        print(f"Fetched {len(all_fields)} / {total}...")
        
        if len(all_fields) >= total or len(results) < limit:
            break
            
        time.sleep(0.5)

    output_path = Path(__file__).resolve().parent / "analyst25_fields.json"
    with open(output_path, "w") as f:
        json.dump(all_fields, f, indent=2)
    print(f"Successfully saved {len(all_fields)} fields to {output_path}")

except Exception as e:
    print(f"Error fetching fields: {e}")

import requests
import urllib3
urllib3.disable_warnings()

url = "https://world-quant.onrender.com/api/status"
headers = {"Authorization": "Bearer yashthakreop"}

try:
    r = requests.get(url, headers=headers, timeout=30, verify=False)
    if r.status_code == 200:
        data = r.json()
        alphas = data.get("alphas", [])
        
        # 1. Pipeline active status
        print("=" * 60)
        print("PIPELINE STATE SUMMARY:")
        print("=" * 60)
        print(f"Pipeline status string: {data.get('status')}")
        print(f"Total alphas in pipeline: {len(alphas)}")
        
        # 2. Count statuses
        counts = {}
        for a in alphas:
            st = a.get("status")
            counts[st] = counts.get(st, 0) + 1
        print(f"Status breakdown: {counts}")
        
        # 3. Print simulating alphas details
        print("\n" + "=" * 60)
        print("ACTIVE SIMULATIONS (SLOTS):")
        print("=" * 60)
        simulating = [a for a in alphas if a.get("status") == "SIMULATING"]
        print(f"Total simulating: {len(simulating)}")
        for idx, a in enumerate(simulating, 1):
            print(f"  {idx:02d}. Slot: {a.get('slot_id')} | Progress: {a.get('progress')}% | Formula: {a['formula'][:80]}...")
            
        # 4. Print pending alphas
        pending = [a for a in alphas if a.get("status") == "PENDING"]
        print(f"\nTotal pending: {len(pending)}")
        
    else:
        print(f"Failed to fetch status: {r.status_code} - {r.text[:300]}")
except Exception as e:
    print(f"Connection failed: {e}")

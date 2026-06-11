import urllib.request
import json
import sys

def fetch_group_alphas(token, group_name):
    url = "http://localhost:8000/api/status"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
            return data.get("alphas", [])
    except Exception as e:
        print(f"Error fetching {group_name}: {e}")
        return []

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    alphas_a = fetch_group_alphas("yashthakreop", "GROUP A")
    alphas_b = fetch_group_alphas("yashthakrepro", "GROUP B")
    
    print("==========================================")
    print("ACTIVE ALPHAS ON LOCALHOST (SLOTS 1-8)")
    print("==========================================\n")
    
    print(f"Group A (Slots 1-4) - Found {len(alphas_a)} alphas:")
    # Group by slot
    for slot in [1, 2, 3, 4]:
        slot_alphas = [a for a in alphas_a if a.get("slot_id") == slot]
        print(f"\n--- SLOT {slot} ---")
        for i, a in enumerate(slot_alphas, 1):
            print(f"  {i}. Status: {a.get('status')} | Sharpe: {a.get('sharpe')} | Fit: {a.get('fitness')}")
            print(f"     Formula: {a.get('formula')}")
            
    print(f"\n\nGroup B (Slots 5-8) - Found {len(alphas_b)} alphas:")
    for slot in [5, 6, 7, 8]:
        slot_alphas = [a for a in alphas_b if a.get("slot_id") == slot]
        print(f"\n--- SLOT {slot} ---")
        for i, a in enumerate(slot_alphas, 1):
            print(f"  {i}. Status: {a.get('status')} | Sharpe: {a.get('sharpe')} | Fit: {a.get('fitness')}")
            print(f"     Formula: {a.get('formula')}")

if __name__ == "__main__":
    main()

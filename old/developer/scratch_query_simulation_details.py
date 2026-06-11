import json
from src.auth import WQSession
from src.client import WQClient

def main():
    print("Initializing WQSession...")
    session = WQSession()
    client = WQClient(session)
    
    # Let's query users/self first to verify active user
    r_self = session.get("https://api.worldquantbrain.com/users/self")
    if r_self.status_code == 200:
        u = r_self.json()
        print(f"Logged in as: {u.get('firstName')} {u.get('lastName')} ({u.get('email')})")
    else:
        print(f"Failed user query: {r_self.status_code} - {r_self.text}")
        return
        
    # Query a list of recent simulations
    # Endpoint: https://api.worldquantbrain.com/simulations?limit=10
    r_sims = session.get("https://api.worldquantbrain.com/simulations?limit=10")
    if r_sims.status_code == 200:
        sims = r_sims.json().get('results', [])
        print(f"\nRecent Simulations (Total: {len(sims)}):")
        for idx, s in enumerate(sims):
            print(f"#{idx+1} | ID: {s.get('id')} | Status: {s.get('status')} | Progress: {s.get('progress')}")
            print(f"  Formula: {s.get('alpha', {}).get('regular', '')[:100]}...")
            if 'message' in s:
                print(f"  Message: {s.get('message')}")
            print("-" * 80)
    else:
        print(f"Failed simulations query: {r_sims.status_code} - {r_sims.text}")

if __name__ == "__main__":
    main()

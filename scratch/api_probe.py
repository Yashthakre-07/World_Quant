import sys
import os
sys.path.append("c:\\Users\\Admin\\Documents\\VIBE_YT\\wq")
from ace_lib import start_session, brain_api_url

def probe_api():
    print("Starting session...")
    try:
        s = start_session()
        print("Session started successfully.")
        
        # Check various endpoints that might contain documentation or Python Alpha info
        endpoints = [
            "/simulations/python-alphas",
            "/documentation",
            "/data-sets",
            "/data-fields"
        ]
        
        for ep in endpoints:
            url = brain_api_url + ep
            print(f"\nChecking endpoint: {url}")
            r = s.get(url)
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                try:
                    data = r.json()
                    # Just print keys or a short preview to not overflow
                    if isinstance(data, dict):
                        print(f"Keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"List of length {len(data)}")
                        if len(data) > 0:
                            print(f"First item keys: {list(data[0].keys())}")
                except Exception as e:
                    print("Could not parse JSON:", e)
                    print(r.text[:200])
            elif r.status_code == 404:
                print("Endpoint not found.")
            else:
                print(f"Response: {r.text[:200]}")
                
    except Exception as e:
        print(f"Error during API probe: {e}")

if __name__ == "__main__":
    probe_api()

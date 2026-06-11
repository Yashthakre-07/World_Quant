import os
import json
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target credentials (Yash)
email = "beyondsynapse@gmail.com"
password = "Web3@ytop"

s = requests.Session()
s.auth = (email, password)

print(f"[AUTH] Authenticating to WorldQuant Brain as {email}...")
r = s.post("https://api.worldquantbrain.com/authentication", verify=False, timeout=20)
print(f"Status Code: {r.status_code}")

if r.status_code == 201:
    print("[AUTH] Successfully authenticated! Querying thematic datasets...")
    
    # 1. Check self profile to see user groups or active competition segments
    print("\n--- Fetching user self profile ---")
    r_self = s.get("https://api.worldquantbrain.com/users/self", verify=False, timeout=20)
    print(f"Status: {r_self.status_code}")
    if r_self.status_code == 200:
        self_data = r_self.json()
        print(f"User: {self_data.get('email')} | Competitions/Themes: {self_data.get('competitions')} | Region: {self_data.get('region')}")
        # Print a clean dump of key fields
        profile_keys = ['id', 'firstName', 'lastName', 'role', 'permissions', 'competitions', 'performanceGroup']
        filtered_profile = {k: self_data.get(k) for k in profile_keys if k in self_data}
        print(json.dumps(filtered_profile, indent=2))
    else:
        print(f"Failed: {r_self.text[:300]}")

    # 2. Check direct /competitions endpoint
    print("\n--- Checking endpoint: https://api.worldquantbrain.com/competitions ---")
    r_comp = s.get("https://api.worldquantbrain.com/competitions", verify=False, timeout=20)
    print(f"Status: {r_comp.status_code}")
    if r_comp.status_code == 200:
        comp_data = r_comp.json()
        results = comp_data.get("results", []) if isinstance(comp_data, dict) else comp_data
        print(f"Competitions found: {len(results)}")
        print(json.dumps(results[:5], indent=2))
    else:
        print(f"Failed: {r_comp.text[:300]}")

    # 3. Query datasets with a theme/competition filter or inspect a sample to find live themes
    print("\n--- Inspecting first 5 active datasets for themes or competitions ---")
    url = "https://api.worldquantbrain.com/data-sets?limit=5"
    r_ds = s.get(url, verify=False, timeout=20)
    if r_ds.status_code == 200:
        datasets = r_ds.json().get("results", [])
        for ds in datasets:
            print(f"\nDataset ID: {ds.get('id')} | Name: {ds.get('name')}")
            print(f"  * Themes: {ds.get('themes')}")
            print(f"  * Competitions: {ds.get('competitions')}")
            print(f"  * Category: {ds.get('category', {}).get('name')} | Subcategory: {ds.get('subcategory', {}).get('name')}")
    else:
        print(f"Failed: {r_ds.text[:300]}")

elif r.status_code == 401:
    if "WWW-Authenticate" in r.headers and r.headers["WWW-Authenticate"] == "persona":
        biometric_url = r.headers.get("Location", "")
        if "api.worldquantbrain.com" in biometric_url:
            biometric_url = biometric_url.replace("api.worldquantbrain.com", "platform.worldquantbrain.com")
        print(f"\n[AUTH] Biometric challenge (Persona) required for this account.")
        print(f"Please open this link in your browser to complete: {biometric_url}")
    else:
        print(f"Failed: {r.text[:300]}")
else:
    print(f"Failed: {r.text[:300]}")

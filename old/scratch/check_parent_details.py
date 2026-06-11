import os
import sys
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    email = "saineela731@gmail.com"
    password = "iitg@123"
    
    s = requests.Session()
    s.auth = (email, password)
    
    # Authenticate to get session token
    auth_res = s.post("https://api.worldquantbrain.com/authentication")
    print("Auth Status:", auth_res.status_code)
    
    url = "https://api.worldquantbrain.com/simulations/4bVFuuaPE4YPczd15c9Bgaqp"
    res = s.get(url)
    print("Parent URL Status:", res.status_code)
    try:
        data = res.json()
        print("\n--- Parent simulation full JSON ---")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    main()

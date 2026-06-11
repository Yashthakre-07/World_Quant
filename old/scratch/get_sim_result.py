import os
import sys
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.path.insert(0, os.getcwd())
import ace_lib

def main():
    os.environ["BRAIN_CREDENTIAL_EMAIL"] = "beyondsynapse@gmail.com"
    os.environ["BRAIN_CREDENTIAL_PASSWORD"] = "Web3@ytop"
    
    session = ace_lib.start_session()
    url = "https://api.worldquantbrain.com/simulations/WzKZV3S04J3apu14CGfzQQd"
    res = session.get(url)
    print("Status:", res.status_code)
    try:
        print(json.dumps(res.json(), indent=2))
    except Exception as e:
        print(res.text)

if __name__ == "__main__":
    main()

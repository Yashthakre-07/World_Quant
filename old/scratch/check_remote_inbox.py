import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SERVERS = {
    "world-quant (Sai Profile)": "https://world-quant.onrender.com/api/inbox-alphas",
    "world-quant-1 (Yash Profile)": "https://world-quant-1.onrender.com/api/inbox-alphas"
}

for name, url in SERVERS.items():
    print(f"Checking review inbox on: {name} ({url}) ...")
    try:
        r = requests.get(url, timeout=30, verify=False)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"[SUCCESS] Found {len(data)} alphas in the review inbox!")
            if data:
                print(f"  * First alpha in inbox: {data[0]['formula']}")
        else:
            print(f"Response Text: {r.text[:300]}")
    except Exception as e:
        print(f"Connection failed: {e}")
    print("-" * 50)

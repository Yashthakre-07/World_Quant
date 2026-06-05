import requests
import time
import urllib3
urllib3.disable_warnings()

url_status = "https://world-quant.onrender.com/api/status"
url_reauth = "https://world-quant.onrender.com/api/reauthenticate"

headers = {
    "Authorization": "Bearer yashthakreop",
    "Content-Type": "application/json"
}

print("Waiting for Render to build and redeploy the update...")
print("Polling status endpoint...")

for attempt in range(1, 30):
    try:
        r = requests.get(url_status, timeout=10, verify=False)
        print(f"Attempt {attempt}: Status Code: {r.status_code}")
        # When Render is redeploying, it might return 502/503 temporarily, or load the old server.
        # Let's hit the reauth endpoint directly to see if the new logic is active.
        if r.status_code == 200:
            print("Server is online! Sending reauthentication request...")
            reauth_res = requests.post(url_reauth, headers=headers, json={}, timeout=15, verify=False)
            print(f"Reauth status code: {reauth_res.status_code}")
            print(f"Reauth response: {reauth_res.text}")
            if "Authenticated Group A instantly" in reauth_res.text:
                print("SUCCESS: New routing code is active and Group A is authenticated!")
                break
    except Exception as e:
        print(f"Attempt {attempt}: Error: {e}")
    time.sleep(10)

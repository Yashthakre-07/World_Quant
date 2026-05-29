import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SERVERS = {
    "world-quant (Sai Profile)": "https://world-quant.onrender.com/api/status",
    "world-quant-1 (Yash Profile)": "https://world-quant-1.onrender.com/api/status"
}

for name, url in SERVERS.items():
    print(f"Checking server: {name} ({url}) ...")
    try:
        r = requests.get(url, timeout=30, verify=False)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Pipeline Status: {data.get('status')}")
            alphas = data.get("alphas", [])
            print(f"Number of alphas in pipeline: {len(alphas)}")
            if alphas:
                completed = sum(1 for a in alphas if a['status'] in ("SUBMITTED", "HARD_REJECT", "SOFT_FAIL", "ERROR"))
                simulating = sum(1 for a in alphas if a['status'] == "SIMULATING")
                pending = sum(1 for a in alphas if a['status'] == "PENDING")
                print(f"  * Completed: {completed}")
                print(f"  * Simulating: {simulating}")
                print(f"  * Pending: {pending}")
                print(f"  * First alpha status: {alphas[0]['status']} - progress: {alphas[0].get('progress')}%")
        else:
            print(f"Response Text: {r.text[:300]}")
    except Exception as e:
        print(f"Connection failed: {e}")
    print("-" * 50)

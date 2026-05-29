import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://world-quant.onrender.com/api/status"
try:
    r = requests.get(url, timeout=30, verify=False)
    if r.status_code == 200:
        data = r.json()
        alphas = data.get("alphas", [])
        print(f"Total Alphas in state: {len(alphas)}")
        for idx, a in enumerate(alphas[:15]):
            print(f"Alpha #{idx+1}: Status={a['status']}, Progress={a.get('progress')}, Sharpe={a.get('sharpe')}, Error={a.get('error_message')[:50] if a.get('error_message') else None}")
    else:
        print(f"HTTP Error: {r.status_code}")
except Exception as e:
    print(f"Failed: {e}")

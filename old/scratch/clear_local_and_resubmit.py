import urllib.request
import json
import time

def clear_and_resubmit():
    base = "http://localhost:8000"
    group = "groupa"
    try:
        with open("scratch/pipeline_state.json", "r", encoding="utf-8") as f:
            p_state = json.load(f)
            group = p_state.get("group", "groupa")
    except Exception:
        pass
        
    token = "yashthakreop" if group == "groupa" else "yashthakrepro"
    print(f"Resubmitting for group: {group} (token: {token})")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 1. Clear Queue
    try:
        req = urllib.request.Request(base + "/api/clear-queue", data=b"{}", headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            print(f"Clear Queue status: {r.status}")
    except Exception as e:
        print(f"Clear Queue error: {e}")

    # 2. Clear Inbox
    try:
        req = urllib.request.Request(base + "/api/clear-inbox", data=b"{}", headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            print(f"Clear Inbox status: {r.status}")
    except Exception as e:
        print(f"Clear Inbox error: {e}")

    time.sleep(2)

    # 3. Load generated alphas
    with open("scratch/generated_alphas.json", "r", encoding="utf-8") as f:
        alphas = json.load(f)

    # 4. Overwrite Queue
    payload_list = []
    for a in alphas:
        payload_list.append({
            "family": a["family"],
            "dataset": a["dataset"],
            "competition": "IQC2025",
            "hypothesis": a["hypothesis"],
            "anomaly_basis": a["anomaly_basis"],
            "formula": a["formula"],
            "settings": {
                "region": "USA",
                "delay": 1,
                "decay": a["decay"],
                "neutralization": "SUBINDUSTRY",
                "universe": "TOP3000",
                "truncation": 0.08
            }
        })

    try:
        req = urllib.request.Request(base + "/api/overwrite-queue", data=json.dumps(payload_list).encode('utf-8'), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"Overwrite Queue status: {r.status}")
            print(f"Response: {r.read().decode('utf-8')}")
    except Exception as e:
        print(f"Overwrite Queue error: {e}")

    time.sleep(2)

    # 5. Trigger start-pipeline
    try:
        req = urllib.request.Request(base + "/api/start-pipeline", data=b"", headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"Start Pipeline status: {r.status}")
    except Exception as e:
        print(f"Start Pipeline error: {e}")

if __name__ == '__main__':
    clear_and_resubmit()

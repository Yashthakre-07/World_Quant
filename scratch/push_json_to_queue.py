import requests
import json
import sys

def submit_alphas(group_name, group_token, group_slots, neutralization, json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        alphas_list = json.load(f)

    print(f"Loaded {len(alphas_list)} alphas for {group_name.upper()}.")

    # Construct payload format expected by overwrite-queue
    payload = []
    for a in alphas_list:
        payload.append({
            "family": a["family"],
            "dataset": a["dataset"],
            "competition": "IQC2025",
            "hypothesis": a["hypothesis"],
            "anomaly_basis": a.get("anomaly_basis", "AI Pattern"),
            "formula": a["formula"],
            "settings": {
                "region": "USA",
                "delay": 1,
                "decay": a.get("decay", 10),
                "neutralization": neutralization,
                "universe": "TOP3000",
                "truncation": 0.08
            }
        })

    url_overwrite = "http://127.0.0.1:8000/api/overwrite-queue"
    url_start = "http://127.0.0.1:8000/api/start-pipeline"
    headers = {"Authorization": f"Bearer {group_token}", "Content-Type": "application/json"}

    try:
        r_over = requests.post(url_overwrite, headers=headers, json=payload, timeout=15)
        print(f"Overwrite Response: {r_over.status_code} - {r_over.text}")
        if r_over.status_code == 200:
            r_start = requests.post(url_start, headers=headers, timeout=15)
            print(f"Start Response: {r_start.status_code} - {r_start.text}")
    except Exception as e:
        print(f"Error submitting payload: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python push_json_to_queue.py <group_name> <token> <slots> <neutralization> <json_file>")
        sys.exit(1)
    submit_alphas(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

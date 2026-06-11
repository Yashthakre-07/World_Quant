import requests

def trigger_login(group_name, token):
    url = "http://127.0.0.1:8000/api/reauthenticate"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print(f"Triggering authentication for {group_name}...")
    try:
        r = requests.post(url, headers=headers, json={}, timeout=60)
        print(f"{group_name} response status: {r.status_code}")
        print(f"Response: {r.text}\n")
    except Exception as e:
        print(f"Failed to connect to server: {e}\n")

if __name__ == "__main__":
    trigger_login("Group A (OPI)", "yashthakreop")
    trigger_login("Group B (OPI-PRO)", "yashthakrepro")

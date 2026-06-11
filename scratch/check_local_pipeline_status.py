import urllib.request
import json

def main():
    base = "http://localhost:8000"
    for name, token in [("Group A", "yashthakreop"), ("Group B", "yashthakrepro")]:
        print(f"\n=== {name} ===")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        try:
            req = urllib.request.Request(base + "/api/queue-status", headers=headers)
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
                print("Queue Status:")
                print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error fetching status: {e}")

if __name__ == '__main__':
    main()

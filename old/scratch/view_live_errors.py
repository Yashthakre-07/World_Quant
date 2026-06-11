import urllib.request
import json

def main():
    url = "http://localhost:8000/api/status"
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer yashthakrepro",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
            alphas = data.get("alphas", [])
            for i, a in enumerate(alphas, 1):
                if a.get("status") == "ERROR":
                    print(f"Alpha #{i} | Slot: {a.get('slot_id')}")
                    print(f"Formula: {a.get('formula')}")
                    print(f"Error: {a.get('error_message') or a.get('error') or 'No detail'}")
                    print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()

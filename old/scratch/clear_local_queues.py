import urllib.request
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    tokens = [("yashthakreop", "GROUP A"), ("yashthakrepro", "GROUP B")]
    
    for token, name in tokens:
        url = "http://localhost:8000/api/clear-queue"
        req = urllib.request.Request(url, data=b"", headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                res = json.loads(r.read().decode('utf-8'))
                print(f"Cleared queue for {name}: {res}")
        except Exception as e:
            print(f"Error clearing queue for {name}: {e}")

if __name__ == "__main__":
    main()

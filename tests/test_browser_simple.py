import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def main():
    try:
        # 1. Health check
        print("Checking server...")
        requests.get(f"{BASE_URL}/docs")
        print("Server up.")
        
        # 2. Browser request
        print("Sending browser command...")
        # Use simpler session id
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": "open url example.com", "session_id": "test_browser"})
        print(r.status_code, r.text)
    except Exception as e:
        print("Failure:", e)

if __name__ == "__main__":
    main()

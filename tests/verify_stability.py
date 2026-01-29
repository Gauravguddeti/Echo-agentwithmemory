import requests
import time

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "stability_test_swap"

def main():
    print("Testing Stability (Swapped)...")
    try:
        # 1. Greeting (Safe?)
        print("Sending 'yo'...")
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": "yo", "session_id": SESSION_ID})
        print(f"Greeting: Status {r.status_code}")
        if r.status_code == 200:
             print("Response:", r.json()['response'])
        
        # 2. Unknown Intent (Risky?)
        print("Sending 'blah blah'...")
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": "blah blah 123", "session_id": SESSION_ID})
        print(f"Unknown Intent: Status {r.status_code}")
        if r.status_code == 200:
             # Should be casual response
             print("Response:", r.json()['response'])
        
        print("Stability Verified.")
    except Exception as e:
        print(f"Crash Detected: {e}")

if __name__ == "__main__":
    main()

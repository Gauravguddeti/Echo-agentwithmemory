import requests
import uuid
import time

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = str(uuid.uuid4())

def msg(text):
    print(f"\nUser: {text}")
    try:
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": text, "session_id": SESSION_ID})
        if r.status_code == 200:
            print(f"Echo: {r.json()['response']}")
            return r.json()['response']
        print(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        print("Msg Error:", e)
    return ""

def main():
    print("--- Testing Phase 8: Browser Nav ---")
    # 1. Open URL
    resp = msg("open url https://example.com")
    if "Navigated to: Example Domain" in resp:
        print("SUCCESS: Browser Opened and Navigated.")
    else:
        print(f"FAILURE: Unexpected response: {resp}")

if __name__ == "__main__":
    main()

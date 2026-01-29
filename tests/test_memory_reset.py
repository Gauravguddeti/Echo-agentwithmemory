import requests
import time

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "test_reset_flow"

def msg(text):
    print(f"\nUser: '{text}'")
    try:
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": text, "session_id": SESSION_ID})
        if r.status_code == 200:
            print(f"Agent: {r.json()['response']}")
            return r.json()['response']
        else:
            print(f"Error: {r.status_code} {r.text}")
    except Exception as e:
        print("Msg Error:", e)

def main():
    # 1. Trigger
    resp1 = msg("clean up ur mem brev")
    if "WARNING" in resp1:
        print("✅ PASS: Triggered Warning.")
    else:
        print("❌ FAIL: No Warning.")
        
    # 2. Confirm
    resp2 = msg("confirm")
    if "Wiped" in resp2:
        print("✅ PASS: Wiped.")
    else:
        print("❌ FAIL: Not Wiped.")

if __name__ == "__main__":
    main()

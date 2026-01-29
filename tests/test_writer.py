import requests
import time

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "test_writer"

def msg(text, label):
    print(f"\n--- {label} ---")
    print(f"User: '{text}'")
    try:
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": text, "session_id": SESSION_ID})
        if r.status_code == 200:
            resp = r.json()['response']
            print(f"Agent: {resp}")
            return resp
        print(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        print("Msg Error:", e)
    return ""

def main():
    print("=== Testing Writer Safety ===")
    
    # 1. Unsafe Write (No App)
    # "type hello" should not just blindly fire keystrokes if we track context/focus?
    # Actually, current impl for 'desktop_write' is: open X + write Y.
    # User requirement: "writing cannot happen into launch commands" (?)
    # "write hello" -> Implicit Notepad?
    # Phase 9 added implicit notepad for "take a note".
    
    # Let's test explicit flow.
    r = msg("open notepad", "1. Open Notepad")
    time.sleep(1)
    
    r = msg("write phase 10 verification to it", "2. Write to Context 'it'")
    # 'it' should resolve to Notepad.
    if "Typed" in r or "Written" in r or "Found window" in r:
         print("✅ PASS: Resolved 'it' -> Notepad and wrote text.")
    else:
         print(f"❌ FAIL: {r}")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()

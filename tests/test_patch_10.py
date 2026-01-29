import requests
import time

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "test_patch_10"

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
    print("=== Testing Phase 10 Patch: Cognitive Stability ===")

    # 1. Greeting (Conversation First)
    r = msg("yo", "1. Greeting")
    # Expect casual response, NO execution error
    if "help" in r.lower() and "assist" in r.lower():
         print("⚠️ WARNING: Too formal?")
    else:
         print("✅ PASS: Casual response.")

    # 2. Filesystem Recovery (Missing Params)
    r = msg("create a folder", "2. Create Folder (Missing Name)")
    # Expect Agent to ask for name
    if "?" in r or "name" in r.lower() or "call it" in r.lower():
         print("✅ PASS: Asked for folder name.")
    else:
         print(f"❌ FAIL: {r}")

    # 3. Unknown Intent
    r = msg("blah blah random noise", "3. Unknown Intent")
    # Expect no crash, just chat
    if "error" in r.lower():
         print(f"❌ FAIL: Crash detected.")
    else:
         print("✅ PASS: Handled unknown intent gracefully.")

    # 4. High Confidence Execution
    r = msg("open notepad", "4. Execution")
    if "Launched" in r or "Opening" in r:
         print("✅ PASS: Executed valid intent.")
    else:
         print(f"❌ FAIL: {r}")
         
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()

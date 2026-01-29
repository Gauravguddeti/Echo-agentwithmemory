import requests
import uuid
import time
import os

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = str(uuid.uuid4())

def msg(text):
    print(f"\nUser: {text}")
    try:
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": text, "session_id": SESSION_ID})
        if r.status_code == 200:
            resp = r.json()['response']
            print(f"Echo: {resp}")
            return resp
        print(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        print("Msg Error:", e)
    return ""

def test_rename():
    print("\n--- Test 7.3: Rename & 7.6 Ambiguity ---")
    # Setup dummy file
    with open("test_rename_me.txt", "w") as f:
        f.write("content")
    
    try:
        # 1. Malformed
        r = msg("rename test_rename_me.txt")
        if "specify format" in r:
            print("PASS: Handled missing arg.")
        else:
            print("FAIL: Bad parsing format.")

        # 2. Correct Request
        r = msg("rename test_rename_me.txt to renamed_success.txt")
        if "ready to rename" in r and "Reply 'Yes'" in r:
            print("PASS: Entered Confirmation.")
        else:
            print("FAIL: Did not confirm.")
            return

        # 3. Confirm
        r = msg("Yes")
        if "Confirmed" in r:
            print("PASS: Executed Rename.")
        else:
            print(f"FAIL: Execution failed: {r}")

        # Verify
        if os.path.exists("renamed_success.txt") and not os.path.exists("test_rename_me.txt"):
             print("PASS: File actually renamed.")
        else:
             print("FAIL: File system state incorrect.")

    finally:
        # Cleanup
        if os.path.exists("test_rename_me.txt"): os.remove("test_rename_me.txt")
        if os.path.exists("renamed_success.txt"): os.remove("renamed_success.txt")

def test_change_intent():
    print("\n--- Test 7.5: Change Intent ---")
    
    # 1. Start Action A
    msg("type hello")
    
    # 2. Switch to Action B (Should overwrite)
    r = msg("type world")
    if "type: 'world'" in r:
         print("PASS: Intent changed to 'world'.")
    else:
         print(f"FAIL: Did not switch intent. Resp: {r}")
         
    # 3. Cancel
    r = msg("cancel")
    if "Cancelled" in r:
        print("PASS: Cancelled successfully.")
    else:
        print("FAIL: Cancel failed.")

def test_web_safe():
    print("\n--- Test 7.1: Web Safe ---")
    r = msg("search python")
    if "Searching" in r:
        print("PASS: Web Search Immediate.")

def main():
    test_web_safe()
    test_change_intent()
    test_rename()

if __name__ == "__main__":
    main()

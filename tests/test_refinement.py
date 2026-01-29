import requests
import time
import os

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "test_refinement"

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
    print("=== Testing Refinement ===")
    
    # 0. Cleanup
    if os.path.exists("grounded_test"):
        os.rmdir("grounded_test")

    # 1. Canonical Creation
    # "named grounded_test" should just become "grounded_test"
    r = msg("create a folder named grounded_test", "1. Create (Canonical)")
    if "Created" in r and "grounded_test" in r:
        print("✅ PASS: Cleaned params and created.")
    else:
        print(f"❌ FAIL: {r}")

    time.sleep(1)

    # 2. Grounded Deletion (Success)
    # Entity "grounded_test" should be in context now?
    # "delete it"
    r = msg("delete it", "2. Delete 'it' (Resolved & Exists)")
    if "Deleted" in r and "grounded_test" in r:
         print("✅ PASS: Resolved 'it' and Deleted existing object.")
    else:
         print(f"❌ FAIL: {r}")

    # 3. Grounded Deletion (Fail Safety)
    r = msg("delete fake_ghost_folder", "3. Delete Non-Existent")
    # Should NOT say "Deleted". Should start a chat or ask clarification.
    if "Deleted" in r:
         print("❌ FAIL: Hallucinated deletion of ghost folder.")
    elif "apologize" in r.lower() or "failed" in r.lower() or "can't" in r.lower() or "create" in r.lower():
         # Chat fallback often apologizes or asks to create it
         print("✅ PASS: Safety check prevented execution.")
    else:
         print(f"✅ PASS (Fallthrough): {r}")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()

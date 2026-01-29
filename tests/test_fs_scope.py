import requests
import time
import uuid
import os
import sys

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = str(uuid.uuid4())

def send_message(message):
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": message, "session_id": SESSION_ID}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def main():
    print(f"Starting Scoped Search Test for Session: {SESSION_ID}")
    
    # Setup: Create 2 dummy files matching 'scope_test'
    files = ["scope_test_A.txt", "scope_test_B.txt"]
    for f in files:
        with open(f, "w") as fh:
            fh.write("dummy content")
    
    # 1. Ambiguous Request
    print(f"\n[Step 1] Requesting: 'Open scope_test'")
    resp1 = send_message("Open scope_test")
    print(f"Echo: {resp1['response']}")
    
    if "multiple matches" in resp1['response'].lower() and "1." in resp1['response']:
        print("SUCCESS: Ambiguity detected and list provided.")
    else:
        print("FAILURE: Did not list candidates.")
        return

    # 2. Selection
    print("\n[Step 2] Selecting: '1'")
    resp2 = send_message("1")
    print(f"Echo: {resp2['response']}")
    
    if "you selected" in resp2['response'].lower() and "reply 'yes'" in resp2['response'].lower():
        print("SUCCESS: Selection accepted, asking for confirmation.")
    else:
        print("FAILURE: Selection flow broken.")
        return

    # 3. Confirmation
    print("\n[Step 3] Confirming: 'Yes'")
    resp3 = send_message("Yes")
    print(f"Echo: {resp3['response']}")
    
    if "confirmed" in resp3['response'].lower() and "opened file" in resp3['response'].lower():
        print("SUCCESS: Action executed.")
    else:
        print("FAILURE: Execution failed.")
        
    # Cleanup
    for f in files:
        try:
            os.remove(f)
        except:
            pass

if __name__ == "__main__":
    main()

import requests
import time
import uuid
import os
import sys
sys.path.append(os.getcwd())
from app.filesystem.trust import get_trust_store

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
    print(f"Starting Filesystem Flow Test for User Session: {SESSION_ID}")
    
    # Setup
    filename = "fs_flow_test.txt"
    with open(filename, "w") as f:
        f.write("Full flow test file.")
    full_path = os.path.abspath(filename)
    
    # Ensure Trust is ASK (Reset)
    store = get_trust_store()
    # We can't delete easily via API, so we manually check if set. 
    # Just Assume default is ASK if path is new (using new filename distinct from prev tests helps).
    # But full_path might ideally be same. Let's force remove from JSON? 
    # Too complex. Let's rely on manual check or set to "ASK" explicitly?
    # TrustStore doesn't handle "reset" via API but set_trust("ASK") is valid if code supports it?
    # No, check_trust returns "ASK" if key missing.
    # Let's assume this path hasn't been trusted yet.
    
    # Refresh Index
    from app.filesystem.index import get_file_index
    idx = get_file_index()
    idx.refresh()
    
    # Step 1: Request "Open fs_flow_test.txt"
    print(f"\n[Step 1] Requesting: 'Open {filename}'")
    resp1 = send_message(f"Open {filename}")
    print(f"Echo: {resp1['response']}")
    
    if "confirm" in resp1['response'].lower():
        print("SUCCESS: Asked for confirmation.")
    else:
        print("FAILURE: Did not ask for confirmation.")
        return

    # Step 2: Confirm "Yes"
    print("\n[Step 2] Sending: 'Yes'")
    resp2 = send_message("Yes")
    print(f"Echo: {resp2['response']}")
    
    if "confirmed" in resp2['response'].lower() and "opened file" in resp2['response'].lower():
        print("SUCCESS: Action Executed.")
    else:
        print("FAILURE: Action not executed properly.")

if __name__ == "__main__":
    main()

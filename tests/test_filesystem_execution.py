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
    print(f"Starting Execution Test for User Session: {SESSION_ID}")
    
    # Setup: Create dummy file
    filename = "fs_test.txt"
    with open(filename, "w") as f:
        f.write("This is a test file for Echo Filesystem Control.")
        
    full_path = os.path.abspath(filename)
    print(f"Created dummy file: {full_path}")
    
    # 1. Pre-authorize content (Simulate user having already trusted this)
    # Because Phase 1E (State) is not ready to handle "Yes".
    store = get_trust_store()
    store.set_trust("open_file", full_path, "GRANTED")
    print("Trust set to GRANTED.")
    
    # 2. Update Index manually? 
    # Index refresher runs on startup or manual call.
    # We should run refresh to ensure file is found.
    from app.filesystem.index import get_file_index
    idx = get_file_index()
    # We only refresh ALLOWED_DIRS=".".
    idx.refresh()
    
    # 3. Send Command
    print("\n[Step 1] Sending Command: 'Open fs_test.txt'")
    resp1 = send_message("Open fs_test.txt")
    print(f"Echo: {resp1['response']}")
    
    if "Opened file" in resp1['response'] or "Executed" in resp1['response']:
        print("SUCCESS: File opened.")
    else:
        print("FAILURE: File not opened (check logs).")

    # Cleanup
    # os.remove(filename)

if __name__ == "__main__":
    main()

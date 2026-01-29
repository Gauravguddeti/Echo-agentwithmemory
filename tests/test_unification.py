import requests
import uuid
import time
import json
import os

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = str(uuid.uuid4())

def send_message(msg):
    try:
        resp = requests.post(f"{BASE_URL}/api/chat", json={"message": msg, "session_id": SESSION_ID})
        if resp.status_code != 200:
             print(f"Server Error {resp.status_code}: {resp.text}")
             return {}
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return {}

def main():
    print("Testing Unification (Memory/Session Control)...")

    # 1. Test Memory Delete ("Forget")
    # First, let's assume there is something to forget. 
    # Or just test the API response for "not found".
    print("\n[Step 1] 'forget zoom'")
    resp1 = send_message("forget zoom")
    print(f"Echo 1: {resp1['response']}")
    
    if "Forgot" in resp1['response'] or "couldn't find" in resp1['response']:
        print("SUCCESS: Forget command handled.")
    else:
        print("FAILURE: Forget command ignored.")

    # 2. Test Quiet Mode
    print("\n[Step 2] 'quiet mode'")
    resp2 = send_message("quiet mode")
    print(f"Echo 2: {resp2['response']}")
    
    if "Switched to Quiet Mode" in resp2['response']:
        print("SUCCESS: Quiet Mode active.")
    else:
        print("FAILURE: Quiet Mode ignored.")

    # 3. Test Reset
    print("\n[Step 3] 'reset chat'")
    resp3 = send_message("reset chat")
    print(f"Echo 3: {resp3['response']}")
    
    if "Context cleared" in resp3['response']:
        print("SUCCESS: Chat Reset.")
    else:
        print("FAILURE: Reset command ignored.")

if __name__ == "__main__":
    main()

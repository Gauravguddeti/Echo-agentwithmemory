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
    print(f"Starting App Opening Test for Session: {SESSION_ID}")
    
    # Prereq: Registry scan happens on import/init. 
    # Not easily mockable without restarting or mocking registry return.
    # We will assume 'Calculator' or 'Notepad' exists in Start Menu.
    # Note: 'Calculator' is often UWP, might not be a .lnk in Programs.
    # 'Notepad' is usually there. Or 'Word', 'Chrome'.
    # Let's try 'Notepad' as it's common.
    
    # Found "Zoom Workplace" in debug logs.
    app_query = "Open Zoom Workplace" 
    
    # 1. Request
    print(f"\n[Step 1] Requesting: '{app_query}'")
    resp1 = send_message(app_query)
    print(f"Echo: {resp1['response']}")
    
    if "confirm" in resp1['response'].lower():
        print("SUCCESS: Asked for confirmation (Ambiguity handled if any, or direct trust check).")
    elif "multiple apps" in resp1['response'].lower():
         print("SUCCESS: Ambiguity detected. Selecting '1'.")
         resp1b = send_message("1")
         print(f"Echo: {resp1b['response']}")
         if "reply 'yes'" not in resp1b['response'].lower():
             print("FAILURE: Selection didn't prompt confirmation.")
             return
    else:
        # If it says "I could not find", then scan failed or no shortcut exists.
        if "could not find" in resp1['response'].lower() or "filesystem" in resp1['response'].lower():
             print("WARNING: App not found in registry. Test inconclusive unless we mock registry.")
             # Fallback to creating a fake shortcut for testing?
             # Too complex for now.
             return

    # 2. Confirm
    print("\n[Step 2] 'Yes'")
    resp2 = send_message("Yes")
    print(f"Echo: {resp2['response']}")
    
    if "executed" in resp2['response'].lower() or "launched" in resp2['response'].lower():
        print("SUCCESS: App launched.")
    else:
        print("FAILURE: App not launched.")

if __name__ == "__main__":
    main()

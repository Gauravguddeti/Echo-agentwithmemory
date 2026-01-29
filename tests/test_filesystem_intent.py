import requests
import time
import uuid

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
    print(f"Starting Filesystem Intent Test for User Session: {SESSION_ID}")
    
    # 1. Test Open File Intent
    print("\n[Step 1] Intent: 'Open budget.pdf'")
    resp1 = send_message("Open budget.pdf")
    print(f"Echo: {resp1['response']}")
    
    # Expect "Intent: open_file" or "Filesystem Intent Detected" in internal logs.
    # User response should acknowledge: "I see you want to open budget.pdf..."
    if "open" in resp1['response'].lower() or "budget" in resp1['response'].lower():
        print("SUCCESS: Intent acknowledged.")
    else:
        print("FAILURE: Intent not acknowledged.")

    # 2. Test Ambiguity (Missing Target)
    print("\n[Step 2] Ambiguity: 'Open the file'")
    resp2 = send_message("Open the file")
    print(f"Echo: {resp2['response']}")
    
    if "which file" in resp2['response'].lower() or "clarify" in resp2['response'].lower():
        print("SUCCESS: Ambiguity detected (Asked for clarification).")
    else:
        print("FAILURE: Did not ask for clarification.")

    # 3. Test Search Intent
    print("\n[Step 3] Intent: 'Find the notes folder'")
    resp3 = send_message("Find the notes folder")
    print(f"Echo: {resp3['response']}")
    
    if "find" in resp3['response'].lower() or "search" in resp3['response'].lower():
        print("SUCCESS: Search intent acknowledged.")
    else:
        print("FAILURE: Search intent not acknowledged.")

if __name__ == "__main__":
    main()

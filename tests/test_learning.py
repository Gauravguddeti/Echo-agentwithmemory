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
    print(f"Starting Learning Test for User Session: {SESSION_ID}")
    
    # 1. Establish initial fact
    print("\n[Step 1] Establishing: 'My favorite color is Blue.'")
    send_message("My favorite color is Blue.")
    time.sleep(2)
    
    # 2. Check recall
    print("\n[Step 2] Checking Recall...")
    resp1 = send_message("What is my favorite color?")
    print(f"Echo: {resp1['response']}")
    
    if "blue" in resp1['response'].lower():
        print("SUCCESS: Remembered Blue.")
    else:
        print("FAILURE: Did not remember Blue.")

    # 3. Issue Correction
    print("\n[Step 3] Issuing Correction: 'No, actually it's Red.'")
    send_message("No, actually it's Red.")
    time.sleep(5) # Wait for background processing
    
    # 4. Check if correction took precedence
    print("\n[Step 4] Checking Recall after Correction...")
    resp2 = send_message("What is my favorite color?")
    print(f"Echo: {resp2['response']}")
    
    if "red" in resp2['response'].lower() and "blue" not in resp2['response'].lower():
        print("SUCCESS: Learned Red and forgot/ignored Blue.")
    elif "red" in resp2['response'].lower():
        print("PARTIAL SUCCESS: Remembered Red, but maybe Blue still mentioned.")
    else:
        print("FAILURE: Did not learn Red.")

if __name__ == "__main__":
    main()

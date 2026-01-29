import requests
import time
import uuid

BASE_URL = "http://127.0.0.1:8000"
USER_ID = f"test-conflict-{uuid.uuid4().hex[:8]}"
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
    print(f"Starting Conflict Test for User Session: {SESSION_ID}")
    
    # Step 1: Establish first fact
    print("\n[Step 1] User: My favorite color is Red.")
    resp1 = send_message("My favorite color is Red.")
    print(f"Echo: {resp1['response']}")
    
    # Wait for background memory write
    print("Waiting 5s for memory sync...")
    time.sleep(5)
    
    # Step 2: Contradict fact
    print("\n[Step 2] User: Actually, I changed my mind. My favorite color is Blue.")
    resp2 = send_message("Actually, I changed my mind. My favorite color is Blue.")
    print(f"Echo: {resp2['response']}")
    
    # Wait for background memory write
    print("Waiting 5s for memory sync...")
    time.sleep(5)
    
    # Step 3: Verify Recall
    print("\n[Step 3] User: What is my favorite color?")
    resp3 = send_message("What is my favorite color?")
    response_text = resp3['response']
    print(f"Echo: {response_text}")
    
    # Verification
    if "Blue" in response_text or "blue" in response_text:
        print("\nSUCCESS: Echo recalled the updated preference (Blue).")
    elif "Red" in response_text or "red" in response_text:
        print("\nFAILURE: Echo recalled the old preference (Red).")
    else:
        print("\nUNCERTAIN: Echo did not mention Red or Blue clearly.")

if __name__ == "__main__":
    main()

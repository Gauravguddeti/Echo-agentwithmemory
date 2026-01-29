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
    print(f"Starting Food Preference Test for User Session: {SESSION_ID}")
    
    # Step 1: State preference
    print("\n[Step 1] User: I like chicken biryani.")
    resp1 = send_message("I like chicken biryani.")
    print(f"Echo: {resp1['response']}")
    
    # Wait for background memory write
    print("Waiting 5s for memory sync...")
    time.sleep(5)
    
    # Step 2: Verify Recall
    print("\n[Step 2] User: What is my favorite food?")
    resp2 = send_message("What is my favorite food?")
    response_text = resp2['response']
    print(f"Echo: {response_text}")
    
    # Verification
    if "biryani" in response_text.lower():
        print("\nSUCCESS: Echo recalled Chicken Biryani.")
    else:
        print("\nFAILURE: Echo did not recall the food preference.")

if __name__ == "__main__":
    main()

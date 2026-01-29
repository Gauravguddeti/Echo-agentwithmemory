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
    print(f"Starting Rerank Test for User Session: {SESSION_ID}")
    
    # Step 1: Add distinct memories
    print("\n[Step 1] Adding memories...")
    send_message("My favorite programming language is Python.")
    time.sleep(2)
    send_message("I love eating pepperoni pizza.")
    time.sleep(5) # Wait for sync
    
    # Step 2: Query about Coding
    print("\n[Step 2] User: What is my favorite programming language?")
    # We expect Python memory to be retrieved and prioritized
    resp1 = send_message("What is my favorite programming language?")
    print(f"Echo: {resp1['response']}")
    
    if "python" in resp1['response'].lower() and "pizza" not in resp1['response'].lower():
        print("SUCCESS: Retrieved Python context correctly.")
    else:
        print("FAILURE: Context retrieval issue (check logs for scores).")

    # Step 3: Query about Food
    print("\n[Step 3] User: What do I like to eat?")
    resp2 = send_message("What do I like to eat?")
    print(f"Echo: {resp2['response']}")
    
    if "pizza" in resp2['response'].lower() and "python" not in resp2['response'].lower():
        print("SUCCESS: Retrieved Pizza context correctly.")
    else:
        print("FAILURE: Context retrieval issue (check logs for scores).")

if __name__ == "__main__":
    main()

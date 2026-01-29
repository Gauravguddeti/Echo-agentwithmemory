import requests
import uuid
import time

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

def test_app(name):
    print(f"\n--- Testing '{name}' ---")
    query = f"Open {name}"
    print(f"Requesting: '{query}'")
    resp = send_message(query)
    print(f"Echo: {resp['response']}")
    
    if "confirm" in resp['response'].lower():
        print("Success: Confirmation prompted.")
        # Confirm it
        resp2 = send_message("Yes")
        print(f"Result: {resp2['response']}")
    elif "multiple" in resp['response'].lower():
        print("Ambiguity. Selecting 1.")
        send_message("1")
        resp3 = send_message("Yes")
        print(f"Result: {resp3['response']}")
    else:
        print("Failure: Did not prompt correctly.")

def main():
    test_app("Task Manager")
    # test_app("Visual Studio Code") # Optional, let's stick to system tool first as requested "other than control panel" context

if __name__ == "__main__":
    main()

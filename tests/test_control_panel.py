import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = str(uuid.uuid4())

def send_message(message):
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": message, "session_id": SESSION_ID}
        )
        return response.json()
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def main():
    query = "Open Control Panel"
    print(f"\n[Step 1] Requesting: '{query}'")
    resp = send_message(query)
    print(f"Echo: {resp['response']}")
    
    if "confirm" in resp['response'].lower() and "control.exe" in resp['response'].lower():
        print("SUCCESS: Control Panel detected and confirmation asked.")
    else:
        print("FAILURE: Did not detect control panel.")
        
    # Step 2: Confirm
    resp2 = send_message("Yes")
    print(f"Echo: {resp2['response']}")
    if "executed" in resp2['response'].lower():
        print("SUCCESS: Launched.")

if __name__ == "__main__":
    main()

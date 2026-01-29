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
    # Test case from user
    query = "open calc brev"
    print(f"\n[Step 1] Requesting: '{query}'")
    resp = send_message(query)
    print(f"Echo: {resp['response']}")
    
    if "confirm" in resp['response'].lower() and "calc.exe" in resp['response'].lower():
        print("SUCCESS: Detected 'calc' in slang.")
        resp2 = send_message("Yes")
        print(f"Result: {resp2['response']}")
    else:
        print("FAILURE: Did not detect calc.")

if __name__ == "__main__":
    main()

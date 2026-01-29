import requests
import uuid
import time
import os

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = str(uuid.uuid4())

def send_message(message):
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": message, "session_id": SESSION_ID}
        )
        if response.status_code != 200:
            print(f"Server Error {response.status_code}: {response.text}")
            return None
        return response.json()
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def main():
    print(f"Starting NLU & Trust Test (Session {SESSION_ID})")
    
    # 1. Normalization Test: "open calc brev" (Slang)
    # Norm -> "open calculator"
    # Fallback to App Scanner if "calculator" not found (or found via registry).
    # Since we added "calculator" alias, it should work.
    
    q1 = "open calc brev"
    print(f"\n[Trip 1] Slang: '{q1}'")
    resp1 = send_message(q1)
    print(f"Echo 1: {resp1['response']}")
    
    if "multiple" in resp1['response'].lower():
        print(">> Ambiguity. Selecting '1' (calc / calculator)...")
        # Select 1
        send_message("1")
        # Confirm
        resp1c = send_message("Yes")
        print(f"Echo 1c: {resp1c['response']}")
        if "opening" in resp1c['response'].lower():
             print("SUCCESS: Trip 1 Executed and Preference should be SAVED.")
    elif "confirm" in resp1['response'].lower():
        print(">> Confirming single match...")
        resp1b = send_message("Yes")
        if "opening" in resp1b['response'].lower():
             print("SUCCESS: Trip 1 Executed.")
             
    # 2. Short-Circuit Test: "open calc" (Standard)
    # Should use saved preference from step 1 and skip menu/ask.
    
    q2 = "open calc"
    print(f"\n[Trip 2] Short-Circuit: '{q2}'")
    resp2 = send_message(q2)
    print(f"Echo 2: {resp2['response']}")
    
    if "opening" in resp2['response'].lower() and "confirm" not in resp2['response'].lower():
        print("SUCCESS: Fast Path triggerred! No confirmation requested.")
    else:
        print("FAILURE: Did not short-circuit.")

    # 3. Semantic Test: "i need maths" -> "open calculator"
    q3 = "i need maths"
    print(f"\n[Trip 3] Semantic: '{q3}'")
    resp3 = send_message(q3)
    print(f"Echo 3: {resp3['response']}")
    if "opening" in resp3['response'].lower():
         print("SUCCESS: Semantic mapping worked & Fast Path reused.")

if __name__ == "__main__":
    main()

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
    print(f"Starting Importance Test for User Session: {SESSION_ID}")
    
    # Step 1: Trivial Statement (Should be discarded)
    print("\n[Step 1] User: The weather is nice today.")
    send_message("The weather is nice today.")
    
    # Wait for background memory write
    print("Waiting 5s for memory sync...")
    time.sleep(5)
    
    # Step 2: Important Statement (Should be stored)
    print("\n[Step 2] User: My favorite hobby is playing guitar.")
    send_message("My favorite hobby is playing guitar.")
    
    print("Waiting 5s for memory sync...")
    time.sleep(5)
    
    # Verification: Check files directly
    import os
    import json
    
    print("\n[Step 4] Checking Memory Files...")
    memory_dir = f"memory/{SESSION_ID}"
    if not os.path.exists(memory_dir):
        print("FAIL: Memory directory not found.")
        return

    files = os.listdir(memory_dir)
    found_guitar = False
    found_weather = False
    
    for f in files:
        if not f.endswith(".json"): continue
        with open(os.path.join(memory_dir, f), "r") as json_file:
            data = json.load(json_file)
            content = data.get("content", "").lower()
            if "guitar" in content:
                found_guitar = True
                print(f"Found Guitar Memory: {content}")
            if "weather" in content:
                found_weather = True
                print(f"Found Weather Memory: {content}")
                
    if found_guitar and not found_weather:
        print("\nSUCCESS: 'Guitar' stored, 'Weather' discarded.")
    elif found_weather:
        print("\nFAILURE: 'Weather' was stored (Low importance filtering failed).")
    else:
        print("\nFAILURE: 'Guitar' was NOT stored.")

if __name__ == "__main__":
    main()

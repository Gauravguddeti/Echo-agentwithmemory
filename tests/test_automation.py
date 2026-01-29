import requests
import uuid
import time
import json

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = str(uuid.uuid4())

def msg(text):
    print(f"User: {text}")
    try:
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": text, "session_id": SESSION_ID})
        if r.status_code == 200:
            print(f"Echo: {r.json()['response']}")
            return r.json()['response']
        print(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        print("Msg Error:", e)
    return ""

def main():
    print("--- Testing Phase 7: Automation ---")
    
    # 1. Web Search (Safe)
    resp = msg("search github copilot")
    if "Searching google" in resp:
        print("SUCCESS: Web search triggered.")
    else:
        print(f"FAILURE: Web search response unexpected: {resp}")

    # 2. Text Input (Unsafe - Confirmation Flow)
    resp = msg("type hello world")
    if "waiting for confirmation" in resp or "ready to type" in resp:
        print("SUCCESS: Entered Confirmation State.")
    else:
        print(f"FAILURE: Did not ask for confirmation: {resp}")
        return

    # 3. Confirm
    resp = msg("yes")
    if "Typed text" in resp:
        print("SUCCESS: Executed Type Command.")
    else:
        print(f"FAILURE: Confirmation failed: {resp}")

if __name__ == "__main__":
    main()

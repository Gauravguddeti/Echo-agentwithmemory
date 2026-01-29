import requests
import time

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "test_vision_01"

def test_screen_vision():
    prompt = "what is on my screen right now?"
    print(f"Sending User Input: {prompt}")
    
    resp = requests.post(f"{BASE_URL}/api/chat", json={
        "message": prompt,
        "session_id": SESSION_ID
    })
    
    if resp.status_code != 200:
        print(f"❌ API Error: {resp.status_code} {resp.text}")
        return

    result = resp.json()['response']
    print(f"Agent Response: {result}")
    
    # Validation logic
    # Look for "YouTube" or "Code" or "Terminal" or typical strings
    if "screen" in result.lower() or "window" in result.lower() or "app" in result.lower() or "nothing" in result.lower():
         print("✅ Agent referenced screen context.")
    else:
         print("⚠️ Agent might not have used perception?")

if __name__ == "__main__":
    test_screen_vision()

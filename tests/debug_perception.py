import requests
import time

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "test_vision_debug"

def test_screen_vision():
    prompt = "what is on my screen right now?"
    
    resp = requests.post(f"{BASE_URL}/api/chat", json={
        "message": prompt,
        "session_id": SESSION_ID
    })
    
    with open("debug_perception_res.txt", "w") as f:
        f.write(f"Status: {resp.status_code}\n")
        f.write(f"Response: {resp.json().get('response', 'No Response')}\n")
        
if __name__ == "__main__":
    test_screen_vision()

import requests
import os
import time

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "test_details_01"

def test_details_creation():
    prompt = " make a txt file in D drive, note her details, she has preetiest eyes, beautifulst smile. "
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
    
    # Check D drive for file
    d_files = os.listdir("D:\\")
    print(f"Files in D:\\: {d_files}")
    
    expected_content_snippet = "smile"
    
    # Valid Candidates
    candidates = ["details.txt", "her_details.txt", "note.txt"]
    
    found = False
    
    for f in d_files:
        if f.endswith(".txt"):
            try:
                path = f"D:\\{f}"
                with open(path, "r", encoding='utf-8', errors='ignore') as fh:
                    content = fh.read()
                    if expected_content_snippet in content or "eyes" in content:
                        print(f"✅ Found content in file: {f}")
                        if len(f) > 30:
                             print(f"❌ FAIL: Filename too long! {f}")
                        else:
                             print(f"✅ PASS: Filename safe: {f}")
                        found = True
                        # Clean up?
                        # os.remove(path)
                        break
            except Exception as e: 
                pass
            
    if not found:
        print("❌ FAIL: File not found or content missing.")

if __name__ == "__main__":
    test_details_creation()

import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "test_habits_01"

def test_habit_creation():
    prompt = "lets note her habits, she is shy when talking to strangers, she loves lily and roses and sunflowers . add this to notes and save it as txt in d drive."
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
    # We expect 'notes.txt' or 'her_habits.txt' or similar short name.
    # We do NOT want 'she is shy....txt'
    
    d_files = os.listdir("D:\\")
    print(f"Files in D:\\: {d_files}")
    
    expected_content_snippet = "sunflowers"
    
    # Heuristic check
    candidates = ["notes.txt", "habits.txt", "her_habits.txt"]
    found = False
    created_file = None
    
    for f in d_files:
        if f.endswith(".txt"):
            # Check modification time? Assuming D is cleanish or we just check content
            try:
                with open(f"D:\\{f}", "r") as fh:
                    content = fh.read()
                    if expected_content_snippet in content:
                        print(f"✅ Found content in file: {f}")
                        created_file = f
                        found = True
                        break
            except: pass
            
    if found:
        if len(created_file) > 30:
             print(f"❌ FAIL: Filename too long! {created_file}")
        else:
             print(f"✅ PASS: Filename safe: {created_file}")
    else:
        print("❌ FAIL: File not found or content missing.")

if __name__ == "__main__":
    test_habit_creation()

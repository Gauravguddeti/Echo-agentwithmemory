import requests
import time
import os

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "test_memory_e2e"

def msg(text, label):
    print(f"\n--- {label} ---")
    print(f"User: '{text}'")
    try:
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": text, "session_id": SESSION_ID})
        if r.status_code == 200:
            resp = r.json()['response']
            print(f"Agent: {resp}")
            return resp
        print(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        print("Msg Error:", e)
    return ""

def main():
    print("=== Testing Memory UI End-to-End ===")
    
    # 1. Implant new Memory
    r = msg("My name is TestUser and I love coding in Python.", "1. Implant Fact")
    print("Waiting for consolidation...")
    time.sleep(10)
    
    # 2. Check UI API
    print("Checking /api/memories...")
    r = requests.get(f"{BASE_URL}/api/memories")
    if r.status_code == 200:
        mems = r.json()
        print(f"Memories found: {len(mems)}")
        found = False
        for m in mems:
             print(f"- Title: {m.get('title')}, Content: {m.get('content')}")
             if "TestUser" in m.get('content', ''):
                 found = True
        
        if found:
             print("✅ PASS: Memory exists and is exposed to UI.")
        else:
             print("❌ FAIL: Memory not found in API list.")
    else:
        print(f"❌ FAIL: API Error {r.status_code}")

    print("\n=== Test Complete ===")
    
if __name__ == "__main__":
    main()

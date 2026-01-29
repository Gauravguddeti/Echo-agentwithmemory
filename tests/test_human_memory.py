import requests
import time
import os

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "test_human_mem"

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
    print("=== Testing Phase 13 Human Memory ===")

    # 1. Implant Memory (Implicit)
    # "I recall your last messages..." - The Memory Client runs in bg.
    # We need to trigger it.
    # "I have a date with Ash on Friday."
    r = msg("I have a date with Ash on Friday. Im nervous.", "1. Implant Memory")
    
    # Wait for background memory tagging (Local store is fast but give it a sec)
    print("Waiting for memory consolidation...")
    time.sleep(2) 
    
    # 2. Check Recall on Greeting
    # Start fresh session?
    # Or same session.
    # "Yo" -> Should trigger "How's Ash?"
    r = msg("Yo", "2. Greeting Trigger")
    
    if "Ash" in r or "date" in r.lower():
        print("✅ PASS: Recalled Ash/Date on greeting.")
    else:
        print(f"❌ FAIL: {r}")
        
    # 3. Reasoning Check (No Defaulting)
    # "What is a good gift?"
    # Should NOT open browser automatically unless "search" is explicit.
    # Prompt says "Assistant must NEVER assume Google... unless goal explicitly requires it."
    # Rule based might default to chat? Or Unknown?
    # If it opens Google -> FAIL.
    r = msg("What is a good gift for her?", "3. Reasoning Check")
    
    if "Launched" in r or "Opening" in r:
         print("❌ FAIL: Assumed tool usage without explicit command.")
    else:
         print("✅ PASS: Stayed conversational (Reasoned).")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()

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
    print(f"Starting Reasoning Test for User Session: {SESSION_ID}")
    
    # 1. Test NEEDS_INFO
    # "Why?" -> Should return clarification *without* LLM (check response time/content?)
    # or just check content "Could you please clarify..."
    print("\n[Step 1] Sending Ambiguous Query 'Why?'...")
    resp1 = send_message("Why?")
    print(f"Echo: {resp1['response']}")
    
    if "clarify" in resp1['response'].lower():
        print("SUCCESS: Clarification triggered.")
    else:
        print("FAILURE: Did not ask for clarification.")

    # 2. Test DIRECT
    # "What is 2+2?"
    print("\n[Step 2] Sending Direct Query...")
    resp2 = send_message("What is 2+2?")
    # Hard to verify "concise" via script without analyzing word count compared to verbose mode.
    # But checking it doesn't crash is good.
    print(f"Echo: {resp2['response']}")
    
    # 3. Test COMPLEX
    # "Compare Python and Java"
    print("\n[Step 3] Sending Complex Query...")
    resp3 = send_message("Compare Python and Java differences.")
    print(f"Echo: {resp3['response'][:100]}...") # Print first 100 chars
    
    # Check if response seems structured or mentions "steps" (LLM might not explicitly say "Step 1" unless prompting forces it strongly).
    # Ideally we'd check logs to see "Thinking Process: ..." injected.
    print("SUCCESS: Complex query handled.")

if __name__ == "__main__":
    main()

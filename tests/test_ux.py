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
    print(f"Starting UX Test for User Session: {SESSION_ID}")
    
    # 1. Complex Query -> Expect BLUF (Summary First)
    print("\n[Step 1] Complex Query: 'Explain the difference between TCP and UDP'")
    resp1 = send_message("Explain the difference between TCP and UDP")
    content1 = resp1['response']
    print(f"Echo:\n{content1[:200]}...") # Printing start to check for Summary
    
    # Check for "Summary" keyword or Bold star pattern
    if "**Summary**" in content1 or "Summary:" in content1:
        print("SUCCESS: BLUF Summary detected.")
    else:
        print("WARNING: BLUF Summary not explicitly found (check formatting).")

    # 2. Direct Query -> Expect Conciseness
    print("\n[Step 2] Direct Query: 'What is the capital of Japan?'")
    resp2 = send_message("What is the capital of Japan?")
    content2 = resp2['response']
    print(f"Echo: {content2}")
    
    if len(content2.split()) < 10:
        print("SUCCESS: Response is concise.")
    else:
        print(f"WARNING: Response might be verbose ({len(content2.split())} words).")

if __name__ == "__main__":
    main()

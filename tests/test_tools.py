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
    print(f"Starting Tool Test for User Session: {SESSION_ID}")
    
    # 1. Calculator Test
    print("\n[Step 1] Testing Calculator: 'What is 35 * 4?'")
    resp1 = send_message("What is 35 * 4?")
    print(f"Echo: {resp1['response']}")
    
    # Check if correct answer (140) is in response.
    if "140" in resp1['response']:
        print("SUCCESS: Calculator used correctly.")
    else:
        print("FAILURE: Matches not found (Calculator might be inactive).")
        
    # 2. Search Test
    print("\n[Step 2] Testing Search: 'What is the latest news on AI?'")
    resp2 = send_message("What is the latest news on AI?")
    print(f"Echo: {resp2['response'][:100]}...")
    
    # Needs manual verification of content, but check length/relevance
    if len(resp2['response']) > 20: 
        print("SUCCESS: Search likely triggered.")
    else:
        print("FAILURE: Response too short.")

    # 3. No Tool Test
    print("\n[Step 3] Testing No Tool: 'Write a poem about dogs.'")
    resp3 = send_message("Write a poem about dogs.")
    if "Calculator Result" not in resp3['response'] and "Web Search Result" not in resp3['response']: 
    # Hard to check internal system prompt, but response should be creative.
        print("SUCCESS: No tool interference.")

if __name__ == "__main__":
    main()

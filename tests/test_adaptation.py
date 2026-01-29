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
    print(f"Starting Adaptation Test for User Session: {SESSION_ID}")
    
    # Session A: Concise User (Short messages)
    print("\n[Step 1] Simulating Concise User (Short inputs)...")
    for _ in range(5):
        resp = send_message("Hi.")
        print(f"User: Hi. | Echo: {resp['response']}")
        time.sleep(0.5)
        
    # Check if response got shorter
    print("\n[Step 2] Sending query to check Conciseness...")
    resp_short = send_message("What is Python?")
    len_short = len(resp_short['response'].split())
    print(f"Echo ({len_short} words): {resp_short['response']}")
    
    if len_short < 50:
        print("SUCCESS: Echo is concise.")
    else:
        print(f"WARNING: Echo is seemingly verbose ({len_short} words).")

    # Session B: Verbose User (Long inputs)
    # We need a new session to reset profile? Or just hammer it with long messages.
    # Profiler uses rolling window of 10. Let's send 12 long messages.
    
    print("\n[Step 3] Simulating Verbose User (Long inputs)...")
    long_msg = "I am extremely interested in the detailed intricacies of the Python programming language and its history dating back to the 1990s."
    for _ in range(12):
        resp = send_message(long_msg)
        print(f"User: [Long] | Echo: {resp['response'][:50]}...")
        time.sleep(0.5)
        
    # Check if response got longer
    print("\n[Step 4] Sending query to check Detail...")
    resp_long = send_message("What is Python?")
    len_long = len(resp_long['response'].split())
    print(f"Echo ({len_long} words): {resp_long['response']}")
    
    if len_long > len_short:
        print("SUCCESS: Echo became more detailed.")
    else:
        print("FAILURE: Echo did not adapt to be more detailed.")

if __name__ == "__main__":
    main()

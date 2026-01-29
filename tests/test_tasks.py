import requests
import uuid
import time
import json
import os

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = str(uuid.uuid4())

def send_message(message):
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": message, "session_id": SESSION_ID}
        )
        return response.json()
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def check_tasks():
    try:
        response = requests.get(f"{BASE_URL}/api/tasks")
        return response.json()
    except:
        return []

def main():
    print("Testing Task Cycle...")
    
    # 1. Create Task (Implicitly)
    print("\n[Step 1] 'open calc'")
    resp1 = send_message("open calc")
    print(f"Echo 1: {resp1['response']}")
    
    # Check if task created
    tasks = check_tasks()
    active = [t for t in tasks if t['status'] == 'active']
    if active:
        print(f"SUCCESS: Active Task Found: {active[0]['intent']}")
    else:
        print("FAILURE: No active task created.")

    # 2. Pause Task
    print("\n[Step 2] 'stop'")
    resp2 = send_message("stop")
    print(f"Echo 2: {resp2['response']}")
    
    tasks = check_tasks()
    paused = [t for t in tasks if t['status'] == 'paused']
    if paused:
        print(f"SUCCESS: Task Paused: {paused[0]['intent']}")
    else:
        print("FAILURE: Task not paused.")

    # 3. Resume Task
    print("\n[Step 3] 'continue'")
    resp3 = send_message("continue")
    print(f"Echo 3: {resp3['response']}")
    
    tasks = check_tasks()
    active_again = [t for t in tasks if t['status'] == 'active']
    if active_again:
         print(f"SUCCESS: Task Resumed: {active_again[0]['intent']}")
    else:
         print("FAILURE: Task not resumed.")

if __name__ == "__main__":
    main()

import requests
import uuid
import time
import json
import os

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = str(uuid.uuid4())

def send_message(msg):
    try:
        resp = requests.post(f"{BASE_URL}/api/chat", json={"message": msg, "session_id": SESSION_ID})
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_tasks():
    try:
        return requests.get(f"{BASE_URL}/api/tasks").json()
    except:
        return []

def main():
    print("Testing Complex Task Switching...")

    # 1. Start Task A (Long running logic not fully impl, but Intent creates task)
    print("\n[Step 1] 'Find requirements.txt' (Task A)")
    send_message("find requirements.txt") # Should create task
    
    tasks = get_tasks()
    task_a = next((t for t in tasks if "find" in t['intent'] and t['status']=='active'), None)
    if task_a:
        print(f"SUCCESS: Task A Created ({task_a['intent']})")
    else:
        print("FAILURE: Task A not active.")

    # 2. Pause Task A implicitly or explicitly?
    # Let's say user interrupts.
    print("\n[Step 2] 'stop'")
    send_message("stop")
    
    tasks = get_tasks()
    task_a = next((t for t in tasks if "find" in t['intent']), None)
    if task_a and task_a['status'] == 'paused':
        print("SUCCESS: Task A Paused.")
    else:
        print(f"FAILURE: Task A status: {task_a['status'] if task_a else 'None'}")

    # 3. Start Task B (Open App - Quick Task)
    print("\n[Step 3] 'Open Calculator' (Task B)")
    resp_b = send_message("open calc")
    print(f"Echo B: {resp_b['response']}")
    
    # Confirm execution to trigger completion
    if "confirm" in resp_b['response'].lower():
        send_message("yes")
        print("Confirmed B.")
        
    tasks = get_tasks()
    # Task B should be COMPLETED (because we launched it)
    task_b = next((t for t in tasks if "open" in t['intent']), None)
    if task_b and task_b['status'] == 'completed':
         print("SUCCESS: Task B Completed.")
    else:
         print(f"FAILURE: Task B status: {task_b['status'] if task_b else 'None'}")

    # 4. Resume Task A
    print("\n[Step 4] 'continue'")
    resp_resume = send_message("continue")
    print(f"Echo Resume: {resp_resume['response']}")
    
    
    tasks = get_tasks()
    task_a = next((t for t in tasks if "find" in t['intent']), None)
    if task_a and task_a['status'] == 'active':
        print("SUCCESS: Task A Resumed (Status Active).")
        # Check if execution happened?
        # The echo should contain the result of "find requirements.txt"
        if "requirements.txt" in resp_resume['response'] or "Found" in resp_resume['response']:
             print("SUCCESS: Search Re-executed!")
        else:
             print("WARNING: Task resumed but output looks empty? (Could be 'Picking up...' only?)")
    else:
        print(f"FAILURE: Task A status: {task_a['status'] if task_a else 'None'}")

if __name__ == "__main__":
    main()

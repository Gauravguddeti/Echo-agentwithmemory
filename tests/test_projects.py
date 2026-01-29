import requests
import uuid
import time
import json

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = str(uuid.uuid4())

def msg(text):
    print(f"User: {text}")
    r = requests.post(f"{BASE_URL}/api/chat", json={"message": text, "session_id": SESSION_ID})
    if r.status_code == 200:
        print(f"Echo: {r.json()['response']}")
        return r.json()['response']
    print(f"Error {r.status_code}: {r.text}")
    return ""

def get_projects():
    return requests.get(f"{BASE_URL}/api/projects").json()

def get_tasks():
    return requests.get(f"{BASE_URL}/api/tasks").json()

def main():
    print("Testing Project Isolation...")
    
    # 1. Start Project A
    msg("start project Alpha")
    projs = get_projects()
    print("DEBUG PROJS:", json.dumps(projs, indent=2))
    
    active = next((p for p in projs if p['status']=='active'), None)
    if not active:
         print("FAILURE: No active project found.")
         return
         
    if "alpha" not in active['name'].lower():
        print(f"FAILURE: Active project is '{active['name']}', expected 'Alpha'.")
        return
    print(f"SUCCESS: Active Project is {active['name']}")
    
    # 2. Add Task to A
    msg("create task check logs")
    tasks_a = get_tasks()
    if len(tasks_a) != 1 or "logs" not in tasks_a[0]['intent']:
        print(f"FAILURE: Task not created or visible. Count: {len(tasks_a)}")
        return
    print("SUCCESS: Task 'check logs' visible in Alpha.")
    
    # 3. Start Project B
    msg("start project Beta")
    projs = get_projects()
    active_b = next((p for p in projs if p['status']=='active'), None)
    if "beta" not in active_b['name'].lower():
        print(f"FAILURE: Beta not active. Active is {active_b['name']}")
        return
    print("SUCCESS: Project Beta started.")
    
    # 4. Check Tasks (Should be empty for Beta initially)
    tasks_b = get_tasks() # Should NOT see 'check logs'
    if len(tasks_b) > 0:
        print(f"FAILURE: Leakage! Seeing tasks from Alpha: {tasks_b}")
        # return # Depending on strictness
    else:
        print("SUCCESS: Task list empty for new project Beta.")
        
    # 5. Add Task to B
    msg("create task read docs")
    tasks_b = get_tasks()
    if len(tasks_b) == 1 and "docs" in tasks_b[0]['intent']:
        print("SUCCESS: Task 'read docs' added to Beta.")
    
    # 6. Switch back to Alpha
    msg("switch to project Alpha")
    
    # 7. Check tasks (Should see 'check logs' again, NOT 'read docs')
    tasks_final = get_tasks()
    intents = [t['intent'] for t in tasks_final]
    
    if "check logs" in str(intents) and "read docs" not in str(intents):
        print("SUCCESS: Context Switched Cleanly back to Alpha.")
    else:
        print(f"FAILURE: Context Switch Error. Visible: {intents}")

if __name__ == "__main__":
    main()

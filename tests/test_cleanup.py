import requests
import uuid
import time
import json

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = str(uuid.uuid4())

def msg(text):
    print(f"User: {text}")
    try:
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": text, "session_id": SESSION_ID})
        if r.status_code == 200:
            print(f"Echo: {r.json()['response']}")
            return r.json()['response']
        print(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        print("Msg Error:", e)
    return ""

def create_junk():
    requests.post(f"{BASE_URL}/api/projects", params={"name": "Junk Proj 1"})
    requests.post(f"{BASE_URL}/api/tasks", params={"intent": "Junk Task 1"}) # Actually create_task via chat is easier but API is not exposed for direct create task easily without auth or context. 
    # Use chat for task creation
    msg("create task garbage collection")

def check_counts():
    projs = requests.get(f"{BASE_URL}/api/projects").json()
    tasks = requests.get(f"{BASE_URL}/api/tasks").json()
    return len(projs), len(tasks)

def main():
    print("Testing Cleanup Phase...")
    
    # 1. Create Junk
    create_junk()
    p_count, t_count = check_counts()
    print(f"State: {p_count} Projects, {t_count} Tasks")
    if p_count <= 1 and t_count == 0:
        print("setup failed?")
    
    # 2. Test API Delete (Simulates Trash Button)
    print("Deleting All Projects via API...")
    requests.delete(f"{BASE_URL}/api/projects")
    
    p_count, _ = check_counts()
    if p_count == 1: # "General" is default
        print("SUCCESS: Projects reset to 1 (General).")
    else:
        print(f"FAILURE: Project count is {p_count}")

    # 3. Test Chat Delete
    msg("create task keep me")
    _, t_count = check_counts()
    if t_count == 0:
        print("Task creation failed")
    
    print("Deleting All Tasks via Chat...")
    # Clear any pending state first
    msg("reset conversation")
    
    resp = msg("delete all tasks")
    
    _, t_count = check_counts()
    if t_count == 0 and "Done" in resp:
        print("SUCCESS: Tasks cleared via Chat.")
    else:
        print(f"FAILURE: Tasks count {t_count}")

if __name__ == "__main__":
    main()

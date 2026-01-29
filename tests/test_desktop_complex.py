import requests
import time
import subprocess

BASE_URL = "http://127.0.0.1:8000"

def msg(text):
    print(f"\nUser: {text}")
    try:
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": text, "session_id": "test_desktop"})
        if r.status_code == 200:
            print(f"Echo: {r.json()['response']}")
            return r.json()['response']
        print(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        print("Msg Error:", e)
    return ""

def main():
    print("--- Testing Phase 9: Desktop Automation ---")
    
    # 1. Close Notepad if open (Clean state)
    subprocess.run("taskkill /F /IM notepad.exe", shell=True, capture_output=True)

    # 2. Command: Open Notepad and Write
    print("Sending command...")
    resp = msg("open notepad and write Automation Test Success")
    
    # 3. Validation
    if "Found window" in resp and "written safely" in resp:
        print("✅ PASS: Launched and Typed Safely.")
    elif "timed out" in resp:
        print("❌ FAIL: Timed out waiting for window.")
    else:
        print(f"❌ FAIL: Unexpected response: {resp}")

    # 4. Cleanup
    time.sleep(2)
    # subprocess.run("taskkill /F /IM notepad.exe", shell=True) 

if __name__ == "__main__":
    main()

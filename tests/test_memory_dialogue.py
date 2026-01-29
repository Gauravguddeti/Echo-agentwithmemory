import requests
import time

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "test_memory_dialogue"

def msg(text, label):
    print(f"\n--- {label} ---")
    print(f"User: '{text}'")
    try:
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": text, "session_id": SESSION_ID})
        if r.status_code == 200:
            print(f"Agent: {r.json()['response']}")
    except Exception as e:
        print("Msg Error:", e)

def check_mems():
    print("\n[Checking Memories]")
    try:
        r = requests.get(f"{BASE_URL}/api/memories")
        mems = r.json()
        print(f"Found {len(mems)} memories.")
        for m in mems:
            print(f"- {m.get('title')}: {m.get('content')}")
        return mems
    except:
        return []

def main():
    # 1. Name
    msg("yoo its gaurav here", "1. Intro")
    
    # 2. Preference
    msg("can call me boss", "2. Preference")
    
    # 3. Date Event
    msg("umm i have a date rn with ash", "3. Date")

    print("\nWaiting for persistence (Sync mode should be instant but give it a sec)...")
    time.sleep(2)
    
    mems = check_mems()
    
    # Validation
    has_gaurav = any("gaurav" in str(m).lower() for m in mems)
    has_boss = any("boss" in str(m).lower() for m in mems)
    has_ash = any("ash" in str(m).lower() for m in mems)
    
    if has_gaurav and has_ash:
        print("\n✅ PASS: Captured Gaurav and Ash.")
    else:
        print(f"\n❌ FAIL: Missing memories. Gaurav={has_gaurav}, Ash={has_ash}")

if __name__ == "__main__":
    main()

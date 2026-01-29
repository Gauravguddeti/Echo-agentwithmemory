import os
import sys
sys.path.append(os.getcwd())
from app.filesystem.trust import get_trust_store

def main():
    print("Testing Trust Store...")
    store = get_trust_store()
    
    action = "open_file"
    path = "d:\\test\\budget.pdf"
    
    # 1. Initial State -> ASK
    print("\n1. Checking initial trust...")
    status = store.check_trust(action, path)
    print(f"Status: {status}")
    if status == "ASK":
        print("SUCCESS: Default is ASK.")
    else:
        print(f"FAILURE: Expected ASK, got {status}")
        
    # 2. Grant Trust
    print("\n2. Granting trust...")
    store.set_trust(action, path, "GRANTED")
    
    # 3. Verify
    print("\n3. Verifying trust...")
    status = store.check_trust(action, path)
    print(f"Status: {status}")
    if status == "GRANTED":
        print("SUCCESS: Trust persisted.")
    else:
        print("FAILURE: Trust not updated.")

    # 4. Deny Trust
    print("\n4. Denying trust...")
    store.set_trust(action, path, "DENIED")
    
    # 5. Verify
    status = store.check_trust(action, path)
    print(f"Status: {status}")
    if status == "DENIED":
        print("SUCCESS: Trust denied.")
    else:
        print("FAILURE: Trust not denied.")

if __name__ == "__main__":
    main()

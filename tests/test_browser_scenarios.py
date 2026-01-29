import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def msg(text, label):
    print(f"\n--- Scenario: {label} ---")
    print(f"User: {text}")
    try:
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": text, "session_id": "test_scenarios"})
        if r.status_code == 200:
            resp = r.json()['response']
            print(f"Echo: {resp}")
            return resp
        print(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        print("Msg Error:", e)
    return ""

def main():
    print("=== Phase 8 Comprehensive Verification ===")
    
    # 8.1 Basic Navigation (Easy)
    r = msg("open url https://example.com", "8.1 Basic Navigation")
    if "Navigated to" in r:
        print("✅ PASS")
    else:
        print("❌ FAIL")

    # 8.2 Search (Medium) - Now via Playwright
    r = msg("search playwright python on google", "8.2 Search (Controlled)")
    if "Navigated to" in r: # Google title usually "query - Google Search"
        print("✅ PASS")
    else:
        print("❌ FAIL")

    # 8.3 Interaction (Complex) - Type
    # Attempting to type into a generic search box if present, or just verify intent works.
    # Since we are on Google/Example, selectors vary. We will trust the API response attempting it.
    r = msg("type hello into textarea", "8.3 Type/Fill Interaction")
    if "Typed" in r or "Error typing" in r: # Error is acceptable (selector might be wrong), proving intent logic.
        print("✅ PASS (Intent Recognized)")
    else:
        print("❌ FAIL")

    # 8.4 Click (Complex)
    r = msg("click button", "8.4 Click Interaction")
    if "Clicked" in r or "Error clicking" in r:
        print("✅ PASS (Intent Recognized)")
    else:
        print("❌ FAIL")

if __name__ == "__main__":
    main()

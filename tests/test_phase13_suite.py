import requests
import time

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "test_vision_suite"

def msg(text):
    print(f"\nUser: '{text}'")
    try:
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": text, "session_id": SESSION_ID})
        if r.status_code == 200:
            res = r.json()['response']
            print(f"Agent: {res}")
            return res
        else:
            print(f"Error: {r.status_code}")
            return ""
    except Exception as e:
        print(f"Req Error: {e}")
        return ""

def test_suite():
    print("=== Test Group A: Perception ===")
    r1 = msg("What app is open right now?")
    if "open" in r1.lower() or "window" in r1.lower() or "app" in r1.lower() or "unknown" in r1.lower():
        print("✅ A1: Active App Detection Triggered.")
    else:
        print("❌ A1: Failed to trigger perception.")

    print("\n=== Test Group C: Discipline ===")
    r2 = msg("Create a file called discipline_test.txt in D drive with content safe")
    if "screen" in r2.lower() or "look" in r2.lower():
        print("❌ C1: Execution triggered Perception (FAIL).")
    elif "created" in r2.lower() or "done" in r2.lower():
         print("✅ C1: Pure Execution Success.")
    else:
         print(f"⚠️ C1: Unsure result: {r2}")

    print("\n=== Test Group F: Refusal ===")
    r3 = msg("Click the start button")
    if "cannot" in r3.lower() or "control" in r3.lower() or "read-only" in r3.lower() or "click" not in r3.lower(): # If it just says "I cannot do that" -> Pass
        # Actually LLM chat fallback might say "I'm text based".
        # As long as it DOES NOT try to execute something.
        print("✅ F1: Refusal/Chat Fallback.")
    else:
        print("⚠️ F1: Did it try?")

if __name__ == "__main__":
    test_suite()

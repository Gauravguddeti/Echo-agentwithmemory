from app.memory_client import add_memory
import time

def test_pipeline():
    print("Testing Memory Pipeline Direct...")
    messages = [
        {"role": "user", "content": "My name is DirectTest and I like logic."},
        {"role": "assistant", "content": "Cool."}
    ]
    try:
        add_memory(messages, "default_user")
        print("add_memory returned.")
    except Exception as e:
        print(f"Pipeline Crash: {e}")

if __name__ == "__main__":
    test_pipeline()

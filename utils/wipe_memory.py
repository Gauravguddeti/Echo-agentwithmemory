import shutil
import os

MEMORY_DIR = "memory"

def clean():
    if os.path.exists(MEMORY_DIR):
        print(f"Wiping {MEMORY_DIR}...")
        shutil.rmtree(MEMORY_DIR)
        print("Memory wiped.")
    else:
        print("Memory clean.")

if __name__ == "__main__":
    clean()

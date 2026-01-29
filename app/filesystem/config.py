import os

# Configurable list of allowed roots.
# Default to current working directory for safety.
# Users can add "D:/Projects", "C:/Users/Name/Documents" etc.
ALLOWED_ROOTS = [
    os.getcwd(), # Current project folder
    # "D:/", # Example (Commented out for safety)
]

def add_root(path: str):
    if os.path.exists(path) and path not in ALLOWED_ROOTS:
        ALLOWED_ROOTS.append(path)

def get_allowed_roots():
    return ALLOWED_ROOTS

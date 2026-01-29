import os
import sys
sys.path.append(os.getcwd())
from app.filesystem.index import get_file_index

def main():
    print("Testing Filesystem Index...")
    index = get_file_index()
    
    # 1. Refresh
    print("1. Refreshing Index...")
    index.refresh()
    
    # 2. Search exact
    print("\n2. Searching for 'requirements.txt'...")
    results = index.search("requirements.txt")
    print(f"Results: {results}")
    
    found = any("requirements.txt" in r[1] for r in results)
    if found:
        print("SUCCESS: Found requirements.txt")
    else:
        print("FAILURE: requirements.txt not found.")
        
    # 3. Resolve Path
    print("\n3. Resolving 'requirements.txt'...")
    paths = index.resolve_path("requirements.txt")
    print(f"Resolved Paths: {paths}")
    
    if paths and os.path.exists(paths[0]):
        print("SUCCESS: Path resolved and exists.")
    else:
        print("FAILURE: Path resolution failed.")

if __name__ == "__main__":
    main()

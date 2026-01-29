import os
import sqlite3
import time

DB_PATH = "filesystem_index.db"
ALLOWED_DIRS = ["."] # Index current directory recursively for safety

class FileIndex:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS files
                     (path TEXT PRIMARY KEY, name TEXT, extension TEXT, modified REAL)''')
        conn.commit()
        conn.close()

    def refresh(self):
        """
        Scans allowed directories and rebuilds index.
        """
        print("Refreshing File Index...")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM files") # Full rebuild for simplicity
        
        count = 0
        for root_dir in ALLOWED_DIRS:
            for root, dirs, files in os.walk(root_dir):
                # skip hidden/venv
                if ".venv" in root or ".git" in root or "__pycache__" in root:
                    continue
                    
                for name in files:
                    full_path = os.path.join(root, name)
                    ext = os.path.splitext(name)[1].lower()
                    mtime = os.path.getmtime(full_path)
                    
                    # Normalize path
                    full_path = os.path.normpath(full_path)
                    
                    c.execute("INSERT OR REPLACE INTO files VALUES (?, ?, ?, ?)",
                              (full_path, name.lower(), ext, mtime))
                    count += 1
        
        conn.commit()
        conn.close()
        print(f"Index Refreshed. {count} files indexed.")

    def search(self, name_query: str) -> list:
        """
        Deterministic search by name substring.
        Returns list of (path, name, ext) tuples.
        """
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Simple LIKE search
        query = f"%{name_query.lower()}%"
        c.execute("SELECT path, name, extension FROM files WHERE name LIKE ? LIMIT 10", (query,))
        results = c.fetchall()
        
        conn.close()
        return results

    def resolve_path(self, target_name: str) -> list:
        """
        Strict resolution. precise match preferred.
        """
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 1. Exact Match
        c.execute("SELECT path FROM files WHERE name = ?", (target_name.lower(),))
        exact = c.fetchall()
        if exact:
            conn.close()
            return [r[0] for r in exact]
            
        # 2. Fuzzy/Substring
        return [r[0] for r in self.search(target_name)]

file_index = FileIndex()

def get_file_index():
    return file_index

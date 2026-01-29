import os
import json
import hashlib

TRUST_FILE = "memory/trust.json"

class TrustStore:
    def __init__(self):
        self._ensure_dir("memory")
        if not os.path.exists(TRUST_FILE):
            with open(TRUST_FILE, "w") as f:
                json.dump({}, f)

    def _ensure_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def _get_hash(self, path: str) -> str:
        return hashlib.md5(path.lower().encode()).hexdigest()

    def check_trust(self, action: str, path: str) -> str:
        """
        Returns 'GRANTED', 'DENIED', or 'ASK'.
        """
        # Destructive actions always ASK initially?
        # Or if we trusted it before, we allow it?
        # User rule: "Trust never escalates automatically for destructive actions."
        # This implies we can save trust for destructive ones if user explicitly says "Remember".
        
        try:
            with open(TRUST_FILE, "r") as f:
                data = json.load(f)
            
            path_hash = self._get_hash(path)
            key = f"{action}:{path_hash}"
            
            if key in data:
                return data[key] # GRANTED or DENIED
                
            return "ASK" # Default
        except Exception as e:
            print(f"Trust Check Error: {e}")
            return "ASK"

    def set_trust(self, action: str, path: str, decision: str):
        """
        decision: 'GRANTED' or 'DENIED'.
        """
        try:
            with open(TRUST_FILE, "r") as f:
                data = json.load(f)
            
            path_hash = self._get_hash(path)
            key = f"{action}:{path_hash}"
            data[key] = decision
            
            with open(TRUST_FILE, "w") as f:
                json.dump(data, f, indent=2)
                
            print(f"Trust Updated: {action} on {path} -> {decision}")
        except Exception as e:
            print(f"Trust Update Error: {e}")

trust_store = TrustStore()

def get_trust_store():
    return trust_store

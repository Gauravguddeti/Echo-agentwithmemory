import os
import json
from typing import Optional

PREFS_FILE = "memory/app_prefs.json"

class AppPreferences:
    def __init__(self):
        self._ensure_dir("memory")
        if not os.path.exists(PREFS_FILE):
            with open(PREFS_FILE, "w") as f:
                json.dump({}, f)
        self.prefs = self._load()

    def _ensure_dir(self, path):
         if not os.path.exists(path):
             os.makedirs(path)

    def _load(self):
        try:
            with open(PREFS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}

    def _save(self):
        try:
            with open(PREFS_FILE, "w") as f:
                json.dump(self.prefs, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")

    def get_preferred_app(self, query: str) -> Optional[str]:
        """
        Returns the path of the preferred app for a given query term.
        e.g. 'zoom' -> 'C:/.../Zoom Workplace.lnk'
        """
        normalized_query = query.lower().strip()
        path = self.prefs.get(normalized_query)
        
        # Validate existence (in case app was uninstalled)
        if path and os.path.exists(path):
            return path
        return None

    def set_preference(self, query: str, path: str):
        """
        Sets a preference for future short-circuiting.
        """
        normalized_query = query.lower().strip()
        self.prefs[normalized_query] = path
        self._save()
        print(f"Preference Saved: '{normalized_query}' -> '{path}'")

prefs = AppPreferences()

def get_app_preferences():
    return prefs

import os
import glob
from typing import Dict, List

class AppRegistry:
    def __init__(self):
        self.apps: Dict[str, str] = {} # Name -> Path
        self.scan()

    def scan(self):
        """
        Scans common Windows Start Menu locations for .lnk files.
        """
        print("Scanning App Registry...")
        self.apps = {}
        
        locations = [
            os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs"),
            os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
        ]
        
        for loc in locations:
            if not os.path.exists(loc):
                continue
                
            # Recursive scan for .lnk
            for root, dirs, files in os.walk(loc):
                for file in files:
                    if file.lower().endswith(".lnk"):
                        # Key: Filename without extension (e.g. "Google Chrome")
                        name = os.path.splitext(file)[0]
                        full_path = os.path.join(root, file)
                        self.apps[name.lower()] = full_path
                        
        # Add basic known tools manually
        sys32 = os.path.join(os.environ["SystemRoot"], "System32")
        self.apps['control panel'] = os.path.join(sys32, "control.exe") 
        self.apps['task manager'] = os.path.join(sys32, "taskmgr.exe")
        self.apps['notepad'] = os.path.join(sys32, "notepad.exe")
        self.apps['cmd'] = os.path.join(sys32, "cmd.exe")
        self.apps['calc'] = os.path.join(sys32, "calc.exe")
        self.apps['calculator'] = os.path.join(sys32, "calc.exe")
        
        print(f"App Registry Scanned: {len(self.apps)} apps found (incl. system tools).")

    def resolve(self, query: str) -> List[str]:
        """
        Returns list of App Names (keys) that match query.
        """
        q = query.lower().strip()
        matches = []
        
        # 1. Exact match
        if q in self.apps:
            matches.append(q)
            
        # 2. Contains match
        for name in self.apps:
            if q in name and name != q:
                 matches.append(name)
                 
        return matches

    def get_path(self, app_name: str) -> str:
        return self.apps.get(app_name.lower())

registry = AppRegistry()

def get_app_registry():
    return registry

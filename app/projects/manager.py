import json
import os
import datetime
from typing import List, Optional
from app.projects.models import Project, ProjectStatus

PROJECTS_FILE = "memory/projects.json"

class ProjectManager:
    def __init__(self):
        self._ensure_dir("memory")
        if not os.path.exists(PROJECTS_FILE):
            # Create default project if none exists?
            # Or just empty list. Let's create a "General" project by default.
            default_proj = Project(name="General", id="default", status=ProjectStatus.ACTIVE)
            self._save_projects([default_proj.dict()])
    
    def _ensure_dir(self, path):
         if not os.path.exists(path):
             os.makedirs(path)

    def _load_projects(self) -> List[dict]:
        try:
            with open(PROJECTS_FILE, "r") as f:
                return json.load(f)
        except:
            return []

    def _save_projects(self, projects: List[dict]):
        with open(PROJECTS_FILE, "w") as f:
            json.dump(projects, f, indent=2)

    def create_project(self, name: str) -> Project:
        projects = self._load_projects()
        
        # Pause current active
        for p in projects:
            if p["status"] == "active":
                p["status"] = "paused"
                p["last_active"] = datetime.datetime.now().isoformat()
        
        new_proj = Project(name=name)
        projects.append(new_proj.dict())
        self._save_projects(projects)
        return new_proj

    def get_projects(self) -> List[Project]:
        data = self._load_projects()
        # Sort by active first, then last_active
        data.sort(key=lambda x: (x["status"] != "active", x["last_active"]), reverse=True) # Sort active to top is complex logic, easier downstream. 
        # Actually: Active (0) < Paused (1). We want Active first.
        # Let's just return list and sort in UI.
        return [Project(**p) for p in data]

    def get_active_project(self) -> Project:
        projects = self._load_projects()
        for p in projects:
            if p["status"] == "active":
                return Project(**p)
        
        # Fallback to default if no active found (safety)
        return Project(name="General", id="default")

    def switch_project(self, project_id: str) -> Optional[Project]:
        projects = self._load_projects()
        target = None
        
        # 1. Check if target exists
        for p in projects:
            if p["id"] == project_id:
                target = p
                break
        
        if not target:
            return None
            
        # 2. Pause current active
        for p in projects:
            if p["status"] == "active":
                p["status"] = "paused"
                p["last_active"] = datetime.datetime.now().isoformat()
        
        # 3. Activate target
        target["status"] = "active"
        target["last_active"] = datetime.datetime.now().isoformat()
        
        self._save_projects(projects)
        return Project(**target)

    def delete_all_projects(self):
        # Reset to default
        default_proj = Project(name="General", id="default", status=ProjectStatus.ACTIVE)
        self._save_projects([default_proj.dict()])
        return {"status": "cleared", "message": "All projects deleted. Reset to General."}

    def delete_batch(self, ids: List[str]):
        projects = self._load_projects()
        # Filter out IDs to delete
        # If active project is deleted, reset to default? Yes, safer.
        
        remaining = [p for p in projects if p["id"] not in ids]
        
        # Check if we need to restore default
        has_active = any(p["status"] == "active" for p in remaining)
        if not remaining or not has_active:
             # Ensure at least one project exists and is active
             if not remaining:
                 default_proj = Project(name="General", id="default", status=ProjectStatus.ACTIVE)
                 remaining = [default_proj.dict()]
             else:
                 # Activate the first one
                 remaining[0]["status"] = "active"
        
        self._save_projects(remaining)
        return {"status": "success", "deleted_count": len(projects) - len(remaining)}

project_manager = ProjectManager()

def get_project_manager():
    return project_manager

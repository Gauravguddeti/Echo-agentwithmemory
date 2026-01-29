import json
import os
import datetime
from typing import List, Optional
from app.tasks.models import Task, TaskStatus

TASKS_FILE = "memory/tasks.json"

class TaskManager:
    def __init__(self):
        self._ensure_dir("memory")
        if not os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "w") as f:
                json.dump([], f)
    
    def _ensure_dir(self, path):
         if not os.path.exists(path):
             os.makedirs(path)

    def _load_tasks(self) -> List[dict]:
        try:
            with open(TASKS_FILE, "r") as f:
                return json.load(f)
        except:
            return []

    def _save_tasks(self, tasks: List[dict]):
        with open(TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=2)

    def create_task(self, intent: str) -> Task:
        tasks = self._load_tasks()
        
        # Get active project
        from app.projects.manager import get_project_manager
        proj_mgr = get_project_manager()
        active_proj = proj_mgr.get_active_project()
        
        # De-activate other active tasks IN THIS PROJECT
        for t in tasks:
            if t["status"] == "active" and t.get("project_id") == active_proj.id:
                t["status"] = "paused"
                t["last_updated"] = datetime.datetime.now().isoformat()
        
        new_task = Task(intent=intent, project_id=active_proj.id)
        tasks.append(new_task.dict())
        self._save_tasks(tasks)
        print(f"Task Created: {intent} ({new_task.id}) in Project: {active_proj.name}")
        return new_task

    def get_tasks(self) -> List[Task]:
        tasks = self._load_tasks()
        
        # Filter by active project
        from app.projects.manager import get_project_manager
        proj_mgr = get_project_manager()
        active_proj = proj_mgr.get_active_project()
        
        filtered = [t for t in tasks if t.get("project_id") == active_proj.id]
        return [Task(**t) for t in filtered]

    def get_active_task(self) -> Optional[Task]:
        # Reuse get_tasks to respect filter
        tasks, _ = self._load_tasks(), None # Need loaded raw for filtering? No, use get_tasks logic
        # Optimize:
        return next((t for t in self.get_tasks() if t.status == TaskStatus.ACTIVE), None)

    def pause_active_task(self) -> Optional[Task]:
        tasks = self._load_tasks()
        
        from app.projects.manager import get_project_manager
        active_proj_id = get_project_manager().get_active_project().id
        
        paused_task = None
        for t in tasks:
            if t["status"] == "active" and t.get("project_id") == active_proj_id:
                t["status"] = "paused"
                t["last_updated"] = datetime.datetime.now().isoformat()
                t["progress"] = "Paused by user"
                paused_task = Task(**t)
        
        if paused_task:
            self._save_tasks(tasks)
            print(f"Task Paused: {paused_task.intent}")
        return paused_task

    def resume_last_paused_task(self) -> Optional[Task]:
        tasks = self._load_tasks()
        # Find most recently updated paused task
        candidates = [t for t in tasks if t["status"] == "paused"]
        if not candidates:
            return None
            
        # Sort by last_updated desc
        candidates.sort(key=lambda x: x["last_updated"], reverse=True)
        target_id = candidates[0]["id"]
        
        resumed_task = None
        for t in tasks:
            if t["id"] == target_id:
                t["status"] = "active"
                t["last_updated"] = datetime.datetime.now().isoformat()
                t["progress"] = "Resuming..."
                resumed_task = Task(**t)
            elif t["status"] == "active":
                # Pause current active if switching
                t["status"] = "paused"
        
        self._save_tasks(tasks)
        print(f"Task Resumed: {resumed_task.intent}")
        return resumed_task

    def complete_active_task(self):
        tasks = self._load_tasks()
        for t in tasks:
            if t["status"] == "active":
                t["status"] = "completed"
                t["progress"] = "Done"
                t["last_updated"] = datetime.datetime.now().isoformat()
        self._save_tasks(tasks)

    def dismiss_completed_tasks(self):
        tasks = self._load_tasks()
        # Keep non-completed
        active_tasks = [t for t in tasks if t["status"] != "completed"]
        self._save_tasks(active_tasks)

    def delete_all_tasks(self):
        self._save_tasks([])

    def delete_batch(self, ids: List[str]):
        tasks = self._load_tasks()
        remaining = [t for t in tasks if t["id"] not in ids]
        self._save_tasks(remaining)
        return {"status": "success", "deleted_count": len(tasks) - len(remaining)}

task_manager = TaskManager()

def get_task_manager():
    return task_manager

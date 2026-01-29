from fastapi import APIRouter, HTTPException
from typing import List
from app.tasks.models import Task
from app.tasks.manager import get_task_manager

router = APIRouter()

@router.get("/tasks", response_model=List[Task])
async def get_tasks():
    manager = get_task_manager()
    return manager.get_tasks()

@router.post("/tasks/{task_id}/control")
async def control_task(task_id: str, action: str):
    manager = get_task_manager()
    
    if action == "pause":
        # We only support pausing active task currently
        # Ideally check ID
        res = manager.pause_active_task()
        return {"status": "paused", "task": res}
        
    elif action == "resume":
        res = manager.resume_last_paused_task() # Limitation: resumes *last*, not specific ID if checked strictly?
        # But UI sends ID. Manager currently blindly resumes last paused. 
        # For Phase 6, let's keep it simple.
        if not res:
            raise HTTPException(status_code=404, detail="No paused task found")
        return {"status": "resumed", "task": res}
        
    elif action == "dismiss":
        manager.dismiss_completed_tasks()
        return {"status": "cleaned"}
        
    raise HTTPException(status_code=400, detail="Invalid action")

@router.delete("/tasks")
async def delete_all_tasks():
    manager = get_task_manager()
    manager.delete_all_tasks()
    return {"status": "cleared"}

from pydantic import BaseModel
class BatchDeleteRequest(BaseModel):
    ids: List[str]

@router.post("/tasks/batch-delete")
async def batch_delete_tasks(req: BatchDeleteRequest):
    manager = get_task_manager()
    return manager.delete_batch(req.ids)

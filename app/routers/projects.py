from fastapi import APIRouter, HTTPException
from typing import List
from app.projects.models import Project
from app.projects.manager import get_project_manager

router = APIRouter()

@router.get("/projects", response_model=List[Project])
async def get_projects():
    manager = get_project_manager()
    return manager.get_projects()

@router.post("/projects")
async def create_project(name: str):
    manager = get_project_manager()
    return manager.create_project(name)

@router.post("/projects/{project_id}/switch")
async def switch_project(project_id: str):
    manager = get_project_manager()
    active = manager.switch_project(project_id)
    if not active:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "switched", "project": active}

@router.delete("/projects")
async def delete_all_projects():
    manager = get_project_manager()
    return manager.delete_all_projects()

from pydantic import BaseModel
class BatchDeleteRequest(BaseModel):
    ids: List[str]

@router.post("/projects/batch-delete")
async def batch_delete_projects(req: BatchDeleteRequest):
    manager = get_project_manager()
    return manager.delete_batch(req.ids)

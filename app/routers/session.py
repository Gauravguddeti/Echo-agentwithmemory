from fastapi import APIRouter, HTTPException, Body
from app.session.manager import get_session_manager
from app.session.models import SessionMode
from pydantic import BaseModel

router = APIRouter()

class ModeRequest(BaseModel):
    mode: SessionMode
    session_id: str

@router.post("/session/mode")
async def set_mode(req: ModeRequest):
    mgr = get_session_manager()
    mgr.set_mode(req.session_id, req.mode)
    return {"status": "updated", "mode": req.mode}

@router.delete("/session/history")
async def clear_history(session_id: str):
    mgr = get_session_manager()
    success = mgr.clear_history(session_id)
    if success:
        return {"status": "cleared"}
    return {"status": "not_found", "message": "No history found"}

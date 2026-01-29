from typing import Optional, Dict
from pydantic import BaseModel

class PendingAction(BaseModel):
    action: str
    path: Optional[str] = None # Can be None if selecting
    destination: Optional[str] = None
    step: str = "confirm" # confirm, select, executing, done
    candidates: Optional[Dict[str, str]] = None # Map "1" -> "path/to/file"
    meta: Optional[dict] = {} # Extra data for automation (e.g. text to type)

class FilesystemState:
    def __init__(self):
        # In-memory simple state. For production, use DB/Key-Value store.
        self.pending_actions: Dict[str, PendingAction] = {}

    def set_pending(self, session_id: str, action: str, path: Optional[str] = None, destination: Optional[str] = None, step: str = "confirm", candidates: Optional[Dict[str, str]] = None, meta: Optional[dict] = None):
        self.pending_actions[session_id] = PendingAction(action=action, path=path, destination=destination, step=step, candidates=candidates, meta=meta)

    def update_pending(self, session_id: str, **kwargs):
        if session_id in self.pending_actions:
            current = self.pending_actions[session_id]
            updated = current.copy(update=kwargs)
            self.pending_actions[session_id] = updated

    def get_pending(self, session_id: str) -> Optional[PendingAction]:
        return self.pending_actions.get(session_id)

    def clear_pending(self, session_id: str):
        if session_id in self.pending_actions:
            del self.pending_actions[session_id]

fs_state = FilesystemState()

def get_fs_state():
    return fs_state

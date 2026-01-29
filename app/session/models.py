from pydantic import BaseModel
from enum import Enum

class SessionMode(str, Enum):
    NORMAL = "normal"
    QUIET = "quiet"
    EXPLAIN = "explain"

class SessionState(BaseModel):
    mode: SessionMode = SessionMode.NORMAL
    # Future: could hold user preferences per session

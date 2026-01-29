from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import uuid
import datetime

class TaskStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    intent: str
    status: TaskStatus = TaskStatus.ACTIVE
    progress: str = "Started"
    created_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    last_updated: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    project_id: str = "default" # New field
    
    # Optional metadata if needed for resumption
    context: Optional[dict] = {}

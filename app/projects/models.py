from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import uuid
import datetime

class ProjectStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    status: ProjectStatus = ProjectStatus.ACTIVE
    summary: str = "New Project"
    root_path: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    last_active: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())

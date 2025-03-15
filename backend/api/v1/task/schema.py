from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class DataCollectionRequest(BaseModel):
    days_back: Optional[int] = 0


class DataCollectionResponse(BaseModel):
    task_id: str
    status: TaskStatus
    message: Optional[str] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[dict] = None
    error: Optional[str] = None

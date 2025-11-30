# app/schemas.py
from pydantic import BaseModel
from typing import Any, Dict, Optional

class RegisterWorker(BaseModel):
    worker_id: str
    name: Optional[str] = None
    capabilities: Optional[Dict[str, Any]] = {}

class CreateTask(BaseModel):
    task_id: str
    workflow_id: Optional[str] = None
    step_id: Optional[str] = None
    payload: Dict[str, Any]

class AssignTask(BaseModel):
    task_id: str
    worker_id: str

class ExecResult(BaseModel):
    task_id: str
    status: str
    output: Dict[str, Any]
# app/api.py
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from .schemas import RegisterWorker, CreateTask, AssignTask, ExecResult
from .db import DB
from .auth import create_token, decode_token, encrypt_key
from .logger import logger
from .worker_client import publish_task
import json
import time

router = APIRouter()

# Health
@router.get("/health")
async def health():
    return {"status": "ok", "time": time.time()}

# Register worker (returns JWT token)
@router.post("/workers/register")
async def register_worker(payload: RegisterWorker):
    # insert or update worker
    await DB.execute(
        "INSERT INTO workers(worker_id, name, capabilities, last_seen, meta) VALUES($1,$2,$3,now(),$4) ON CONFLICT (worker_id) DO UPDATE SET last_seen = now(), name=EXCLUDED.name, capabilities=EXCLUDED.capabilities RETURNING worker_id",
        payload.worker_id, payload.name, json.dumps(payload.capabilities), json.dumps({})
    )
    token = create_token({"worker_id": payload.worker_id})
    logger.info({"event": "worker_registered", "worker_id": payload.worker_id})
    return {"worker_id": payload.worker_id, "token": token}

# Store API key (encrypted) for external services (admin endpoint)
@router.post("/apikeys/{service_name}")
async def store_api_key(service_name: str, key_payload: dict):
    # key_payload: {"key": "..."} ; encrypt and store
    key = key_payload.get("key")
    if not key:
        raise HTTPException(status_code=400, detail="missing key")
    enc = encrypt_key(key)
    await DB.execute("INSERT INTO api_keys(service_name, encrypted_key) VALUES($1,$2) ON CONFLICT (service_name) DO UPDATE SET encrypted_key=EXCLUDED.encrypted_key", service_name, enc)
    return {"status": "ok"}

# Create task
@router.post("/tasks/create")
async def create_task(req: CreateTask):
    await DB.execute("INSERT INTO tasks(task_id, workflow_id, step_id, payload, status, created_at, updated_at) VALUES($1,$2,$3,$4,$5,now(),now())",
                     req.task_id, req.workflow_id, req.step_id, json.dumps(req.payload), "PENDING")
    # publish to Redis so workers pick up
    await publish_task({"task_id": req.task_id, "workflow_id": req.workflow_id, "step_id": req.step_id, "payload": req.payload})
    logger.info({"event": "task_created", "task_id": req.task_id})
    return {"task_id": req.task_id, "status": "PENDING"}

# Assign a task to a worker (manual)
@router.post("/tasks/assign")
async def assign_task(req: AssignTask):
    await DB.execute("UPDATE tasks SET assigned_worker=$1, status=$2, updated_at=now() WHERE task_id=$3", req.worker_id, "ASSIGNED", req.task_id)
    logger.info({"event": "task_assigned", "task_id": req.task_id, "worker": req.worker_id})
    # optionally publish to worker channel
    await publish_task({"task_id": req.task_id, "assigned_to": req.worker_id})
    return {"task_id": req.task_id, "assigned_to": req.worker_id}

# Worker posts execution result
@router.post("/tasks/result")
async def task_result(res: ExecResult, x_worker_token: Optional[str] = Header(None)):
    # validate token
    if not x_worker_token:
        raise HTTPException(status_code=401, detail="Missing worker token")
    try:
        claims = decode_token(x_worker_token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    worker_id = claims.get("worker_id")
    # update task
    await DB.execute("UPDATE tasks SET status=$1, logs = logs || $2::jsonb, updated_at=now() WHERE task_id=$3", res.status, json.dumps([res.output]), res.task_id)
    logger.info({"event": "task_result", "task_id": res.task_id, "worker": worker_id, "status": res.status})
    return {"status": "ok"}
# app/main.py
import asyncio
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.db import DB
from app.api import router as api_router
from app.logger import logger

# Optional: worker task listener (workers can subscribe)
from app.worker_client import RedisClient
import json


load_dotenv()

app = FastAPI(title="MCP - Message Coordination Platform", version="1.0.0")

# Allow any internal calls (you can limit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach API routes
app.include_router(api_router)


# BACKGROUND REDIS LISTENER (optional)
async def redis_listener():
    """
    MCP Redis listener to observe worker responses / debugging.
    Workers will publish results into 'worker_results' channel.
    """
    try:
        r = await RedisClient.get()
        pubsub = r.pubsub()
        await pubsub.subscribe("worker_results")

        logger.info({"event": "redis_listener_started"})

        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    logger.info({"event": "worker_result", "data": data})
                except Exception as e:
                    logger.error({"error": str(e)})
    except Exception as e:
        logger.error({"error": str(e)})


# STARTUP
@app.on_event("startup")
async def startup():
    logger.info({"event": "startup_begin"})

    # connect DB pool
    await DB.connect()
    logger.info({"event": "db_connected"})

    # Run migrations
    import pathlib
    base = pathlib.Path(__file__).parent.parent / "migrations"
    files = sorted([p for p in base.glob("*.sql")])
    for f in files:
        sql = f.read_text()
        await DB.execute(sql)
    logger.info({"event": "migrations_completed"})

    # launch redis listener in background
    asyncio.create_task(redis_listener())
    logger.info({"event": "redis_listener_task_spawned"})

    logger.info({"event": "startup_complete"})


# SHUTDOWN
@app.on_event("shutdown")
async def shutdown():
    await DB.close()
    logger.info({"event": "mcp_shutdown"})


# Root endpoint
@app.get("/")
async def root():
    return {"service": "MCP", "status": "running"}
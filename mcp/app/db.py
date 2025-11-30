# app/db.py
import os
import asyncpg
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

POSTGRES_DSN = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

class DB:
    _pool: Optional[asyncpg.pool.Pool] = None

    @classmethod
    async def connect(cls):
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(dsn=POSTGRES_DSN, min_size=1, max_size=10)
        return cls._pool

    @classmethod
    async def close(cls):
        if cls._pool:
            await cls._pool.close()
            cls._pool = None

    @classmethod
    async def execute(cls, query: str, *args):
        pool = await cls.connect()
        async with pool.acquire() as conn:
            return await conn.execute(query, *args)

    @classmethod
    async def fetch(cls, query: str, *args):
        pool = await cls.connect()
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(r) for r in rows]

    @classmethod
    async def fetchrow(cls, query: str, *args):
        pool = await cls.connect()
        async with pool.acquire() as conn:
            r = await conn.fetchrow(query, *args)
            return dict(r) if r else None
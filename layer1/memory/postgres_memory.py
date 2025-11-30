from __future__ import annotations
from typing import Any, Dict, Optional, List
import psycopg2
import psycopg2.extras

class PostgresMemory:
    """
    Structured Memory using PostgreSQL
    """

    def __init__(self, host: str = "localhost", port: int = 5432, dbname: str = "agent_db",
                 user: str = "postgres", password: str = "postgres"):
        self.conn = psycopg2.connect(
            host=host, port=port, dbname=dbname, user=user, password=password
        )
        self.conn.autocommit = True

    def insert(self, table: str, data: Dict[str, Any]):
        keys = data.keys()
        values = [data[k] for k in keys]
        query = f"INSERT INTO {table} ({', '.join(keys)}) VALUES ({', '.join(['%s']*len(keys))})"
        with self.conn.cursor() as cur:
            cur.execute(query, values)

    def fetch_one(self, table: str, where: str, params: Optional[List[Any]] = None) -> Optional[Dict[str, Any]]:
        query = f"SELECT * FROM {table} WHERE {where} LIMIT 1"
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params or [])
            return cur.fetchone()

    def fetch_all(self, table: str, where: str = "TRUE", params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM {table} WHERE {where}"
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params or [])
            return cur.fetchall()

    def update(self, table: str, data: Dict[str, Any], where: str, params: Optional[List[Any]] = None):
        keys = data.keys()
        values = [data[k] for k in keys]
        set_clause = ", ".join([f"{k}=%s" for k in keys])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        with self.conn.cursor() as cur:
            cur.execute(query, values + (params or []))

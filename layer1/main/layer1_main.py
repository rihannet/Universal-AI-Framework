from __future__ import annotations
from typing import Optional
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from planner.planner_main import Layer1Planner
from planner.core.state import PlannerState
from memory.memory_facade import MemoryFacade
from memory.redis_memory import RedisMemory
from state_manager.state_facade import StateManagerFacade
from state_manager.redis_connector import RedisConnector
from llm_engine.llm_engine_main import Layer1LLMEngine
from llm_engine.llm_connector import LMStudioConnector


class Layer1Main:
    """
    Main Layer-1 aggregator.
    Combines:
    - Planner (graph-based workflow planning)
    - MemoryFacade (Redis + Pinecone + PostgreSQL)
    - StateManagerFacade (Redis runtime state)
    - LLM Engine (DeepSeek-R1-Qwen3-8B via LM Studio)
    """

    def __init__(
        self,
        lmstudio_base_url: Optional[str] = None,
        redis_host: Optional[str] = None,
        redis_port: Optional[int] = None,
        enable_vector_memory: bool = False
    ):
        # Use environment variables with fallback defaults
        lmstudio_base_url = lmstudio_base_url or os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234")
        redis_host = redis_host or os.getenv("REDIS_HOST", "localhost")
        redis_port = redis_port or int(os.getenv("REDIS_PORT", "6379"))
        # Initialize LLM Engine
        self.llm_engine = Layer1LLMEngine()
        connector = LMStudioConnector(base_url=lmstudio_base_url)
        self.llm_engine.bind_lmstudio(connector)

        # Initialize Memory
        redis_mem = RedisMemory(host=redis_host, port=redis_port)
        self.memory = MemoryFacade(redis=redis_mem, enable_vector=enable_vector_memory)

        # Initialize State Manager
        redis_conn = RedisConnector(host=redis_host, port=redis_port)
        self.state_manager = StateManagerFacade(redis_connector=redis_conn)

        # Initialize Planner with bindings
        self.planner = Layer1Planner()
        self.planner.register_llm(self.llm_engine.llm)
        self.planner.register_memory(self.memory)

    # ---------------------- Workflow API ----------------------
    def create_workflow(self, user_id: str, goal: str, context: Optional[dict] = None) -> PlannerState:
        """Create a new workflow"""
        state = self.planner.create_workflow(user_id=user_id, goal=goal, context=context)
        self.state_manager.set_workflow_state(state.workflow_id, state.status)
        return state

    def plan_workflow(self, state: PlannerState) -> PlannerState:
        """Execute planner to generate steps"""
        state = self.planner.plan_workflow(state)
        self.state_manager.set_workflow_state(state.workflow_id, state.status)
        return state

    # ---------------------- Memory API ----------------------
    def save_temp_memory(self, key: str, value: str, ttl: Optional[int] = None):
        """Save to short-term memory (Redis)"""
        self.memory.set_temp(key, value, ttl)

    def get_temp_memory(self, key: str) -> Optional[str]:
        """Retrieve from short-term memory"""
        return self.memory.get_temp(key)

    # ---------------------- State API ----------------------
    def set_workflow_state(self, workflow_id: str, state: str):
        """Update workflow state"""
        self.state_manager.set_workflow_state(workflow_id, state)

    def get_workflow_state(self, workflow_id: str) -> Optional[str]:
        """Get workflow state"""
        return self.state_manager.get_workflow_state(workflow_id)

    def assign_task(self, task_id: str, worker_id: str):
        """Assign task to worker"""
        self.state_manager.assign_task(task_id, worker_id)

    # ---------------------- LLM API ----------------------
    def llm_call(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """Direct LLM call"""
        return self.llm_engine.llm(prompt, max_tokens=max_tokens, temperature=temperature)

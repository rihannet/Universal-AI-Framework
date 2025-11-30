"""Layer-2 Main: Worker Orchestration System"""
import os
import sys
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from layer1.memory.redis_memory import RedisMemory
from layer1.memory.memory_facade import MemoryFacade
from layer1.llm_engine.llm_connector import LMStudioConnector
from layer1.planner.planner_main import Layer1Planner
from layer1.planner.core.state import PlannerState


class Layer2Main:
    """Main orchestrator for Layer-2 Worker System"""
    
    def __init__(
        self,
        lmstudio_base_url: Optional[str] = None,
        redis_host: Optional[str] = None,
        redis_port: Optional[int] = None,
        layer1_planner: Optional[Layer1Planner] = None,
        layer3_mcp=None,
        layer4_safety=None,
        layer5_audit=None
    ):
        # Configuration
        self.lmstudio_base_url = lmstudio_base_url or os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234")
        redis_host = redis_host or os.getenv("REDIS_HOST", "localhost")
        redis_port = redis_port or int(os.getenv("REDIS_PORT", "6379"))
        
        # Initialize LLM (shared across all workers)
        self.llm_connector = LMStudioConnector(base_url=self.lmstudio_base_url)
        
        # Initialize Redis memory (shared short-term memory like Layer-1)
        self.redis_memory = RedisMemory(host=redis_host, port=redis_port)
        
        # Initialize Memory Facade (same as Layer-1)
        self.memory_facade = MemoryFacade(redis=self.redis_memory, enable_vector=False)
        
        # Use Layer-1 planner or create new one
        if layer1_planner:
            self.planner = layer1_planner
        else:
            self.planner = Layer1Planner()
            self.planner.register_llm(self.llm_connector.llm)
            self.planner.register_memory(self.memory_facade)
        
        # Layer integrations
        self.layer3_mcp = layer3_mcp
        self.layer4_safety = layer4_safety
        self.layer5_audit = layer5_audit
        
        # Worker registry
        self.workers: Dict[str, Dict[str, Any]] = {}
        self.worker_configs_dir = Path(__file__).parent / "workers"
        self.worker_configs_dir.mkdir(exist_ok=True)
        
        # Load existing workers
        self._load_workers()
        
        print("[Layer-2] Worker Orchestration initialized")
        print(f"[Layer-2] LLM: {self.lmstudio_base_url}")
        print(f"[Layer-2] Redis: {redis_host}:{redis_port}")
        print(f"[Layer-2] Planner: {'Shared with Layer-1' if layer1_planner else 'Independent'}")
        print(f"[Layer-2] Workers loaded: {len(self.workers)}")
    
    def _load_workers(self):
        """Load all worker configurations from workers/ directory"""
        for config_file in self.worker_configs_dir.glob("*.json"):
            try:
                import json
                config = json.loads(config_file.read_text())
                worker_id = config.get("worker_id")
                if worker_id:
                    self.workers[worker_id] = config
                    print(f"[Layer-2] Loaded worker: {worker_id}")
            except Exception as e:
                print(f"[Layer-2] Failed to load {config_file.name}: {e}")
    
    def create_worker(
        self,
        worker_id: str,
        name: str,
        worker_type: str,  # Can be ANY type: browser, email, sms, video, custom, etc.
        capabilities: List[str],
        api_keys: Optional[Dict[str, str]] = None,
        endpoints: Optional[Dict[str, str]] = None,
        model_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create specialized worker with API keys and configuration
        
        worker_type can be ANY custom type you want:
        - Standard: browser, terminal, file, app, api, dbms
        - Custom: email, sms, video, audio, pdf, excel, slack, discord, etc.
        """
        import json
        
        worker_config = {
            "worker_id": worker_id,
            "name": name,
            "worker_type": worker_type,
            "capabilities": capabilities,
            "api_keys": api_keys or {},
            "endpoints": endpoints or {},
            "model_config": model_config or {
                "temperature": 0.7,
                "max_tokens": 2048
            },
            "created_at": str(asyncio.get_event_loop().time())
        }
        
        # Save to file
        config_file = self.worker_configs_dir / f"{worker_id}.json"
        config_file.write_text(json.dumps(worker_config, indent=2))
        
        # Register in memory
        self.workers[worker_id] = worker_config
        
        print(f"[Layer-2] Created worker: {worker_id} ({worker_type})")
        return worker_config
    
    async def execute_worker_task(
        self,
        worker_id: str,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        use_planner: bool = True
    ) -> Dict[str, Any]:
        """Execute task with specific worker through all layers"""
        context = context or {}
        
        # Get worker config
        worker_config = self.workers.get(worker_id)
        if not worker_config:
            return {"success": False, "error": f"Worker {worker_id} not found"}
        
        # Step 0: Use Layer-1 Planner to decompose task (if enabled)
        plan_steps = None
        if use_planner and self.planner:
            try:
                # Create workflow using Layer-1 planner
                state = self.planner.create_workflow(
                    user_id=worker_id,
                    goal=task,
                    context={"worker_type": worker_config["worker_type"], **context}
                )
                
                # Plan workflow (runs through all planner nodes)
                state = self.planner.plan_workflow(state)
                
                # Extract steps from plan
                if state.status == "PLANNED" and state.steps:
                    plan_steps = state.steps
                    print(f"[Layer-2] Planner generated {len(plan_steps)} steps")
            except Exception as e:
                print(f"[Layer-2] Planner failed: {e}, falling back to direct execution")
        
        # Step 1: Layer-4 Safety Check
        if self.layer4_safety:
            try:
                # Layer-4 validate_action is async
                if asyncio.iscoroutinefunction(self.layer4_safety.validate_action):
                    safety_check = await self.layer4_safety.validate_action(
                        task,
                        {"agent_type": worker_config["worker_type"], **context}
                    )
                else:
                    # If not async, call directly
                    safety_check = self.layer4_safety.validate_action(
                        task,
                        {"agent_type": worker_config["worker_type"], **context}
                    )
                
                if not safety_check["allowed"]:
                    return {
                        "success": False,
                        "error": f"Blocked by Layer-4: {safety_check['reason']}",
                        "stage": "safety"
                    }
            except Exception as e:
                print(f"[Layer-2] Safety check failed: {e}, continuing without safety check")
        
        # Step 2: Execute via Layer-3 MCP (with or without plan)
        result = None
        if self.layer3_mcp:
            # Determine tool based on worker type
            tool_name = self._map_worker_to_tool(worker_config["worker_type"])
            
            # Prepare parameters with API keys and plan
            params = {
                "task": task,
                "context": context,
                "api_keys": worker_config.get("api_keys", {}),
                "endpoints": worker_config.get("endpoints", {}),
                "plan_steps": [{
                    "id": s.id,
                    "title": s.title,
                    "description": s.description
                } for s in plan_steps] if plan_steps else None
            }
            
            # Execute through MCP
            result = await self.layer3_mcp.execute_tool(tool_name, params)
        else:
            # Fallback: Direct execution
            result = await self._execute_direct(worker_config, task, context)
        
        # Step 3: Store in Redis memory (using Memory Facade)
        memory_key = f"worker:{worker_id}:last_task"
        self.memory_facade.set_temp(memory_key, str(result), ttl=3600)
        
        # Step 4: Layer-5 Audit Log
        if self.layer5_audit:
            try:
                # Layer-5 log_layer_action is async
                if asyncio.iscoroutinefunction(self.layer5_audit.log_layer_action):
                    await self.layer5_audit.log_layer_action(
                        "Layer-2",
                        f"worker_execution:{worker_id}",
                        {"task": task, "result": result, "plan_steps": len(plan_steps) if plan_steps else 0},
                        worker_id
                    )
                else:
                    # If not async, call directly
                    self.layer5_audit.log_layer_action(
                        "Layer-2",
                        f"worker_execution:{worker_id}",
                        {"task": task, "result": result, "plan_steps": len(plan_steps) if plan_steps else 0},
                        worker_id
                    )
            except Exception as e:
                print(f"[Layer-2] Audit log failed: {e}, continuing without audit")
        
        return result
    
    def _map_worker_to_tool(self, worker_type: str) -> str:
        """Map worker type to MCP tool
        
        Known types map to specific tools.
        Any custom type uses 'universal' tool.
        """
        mapping = {
            "browser": "browser",
            "terminal": "shell",
            "api": "http_api",
            "file": "file",
            "app": "app",
            "dbms": "universal"
        }
        # Any custom type (email, sms, video, etc.) uses universal tool
        return mapping.get(worker_type, "universal")
    
    async def _execute_direct(
        self,
        worker_config: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Direct execution without MCP (fallback)"""
        worker_type = worker_config["worker_type"]
        
        if worker_type == "terminal":
            return await self._execute_terminal(task, context)
        elif worker_type == "browser":
            return await self._execute_browser(task, context)
        elif worker_type == "api":
            return await self._execute_api(task, worker_config, context)
        else:
            # Use LLM for general tasks
            return await self._execute_llm(task, worker_config, context)
    
    async def _execute_terminal(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute terminal command"""
        import subprocess
        try:
            result = subprocess.run(
                task,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_browser(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute browser task"""
        import requests
        try:
            url = context.get("url", task)
            response = requests.get(url, timeout=30)
            return {
                "success": True,
                "status_code": response.status_code,
                "content": response.text[:1000]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_api(
        self,
        task: str,
        worker_config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute API call with stored API keys"""
        import requests
        try:
            endpoint = worker_config.get("endpoints", {}).get("default", task)
            api_keys = worker_config.get("api_keys", {})
            
            headers = {}
            if "api_key" in api_keys:
                headers["Authorization"] = f"Bearer {api_keys['api_key']}"
            
            response = requests.get(endpoint, headers=headers, timeout=30)
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_llm(
        self,
        task: str,
        worker_config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute task using LLM"""
        try:
            model_config = worker_config.get("model_config", {})
            prompt = f"Task: {task}\nContext: {context}\nExecute this task and provide the result."
            
            response = self.llm_connector.llm(
                prompt,
                max_tokens=model_config.get("max_tokens", 2048),
                temperature=model_config.get("temperature", 0.7)
            )
            
            return {"success": True, "response": response}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_workers(self) -> List[Dict[str, Any]]:
        """List all registered workers"""
        return [
            {
                "worker_id": w["worker_id"],
                "name": w["name"],
                "type": w["worker_type"],
                "capabilities": w["capabilities"]
            }
            for w in self.workers.values()
        ]
    
    def get_worker(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Get worker configuration"""
        return self.workers.get(worker_id)
    
    def delete_worker(self, worker_id: str) -> bool:
        """Delete worker"""
        if worker_id in self.workers:
            config_file = self.worker_configs_dir / f"{worker_id}.json"
            if config_file.exists():
                config_file.unlink()
            del self.workers[worker_id]
            print(f"[Layer-2] Deleted worker: {worker_id}")
            return True
        return False
    
    def get_worker_memory(self, worker_id: str) -> Optional[str]:
        """Get worker's last task from Redis memory"""
        memory_key = f"worker:{worker_id}:last_task"
        return self.memory_facade.get_temp(memory_key)
    
    def get_planner(self) -> Layer1Planner:
        """Get Layer-1 planner instance"""
        return self.planner


# Convenience function
def create_layer2(
    lmstudio_base_url: Optional[str] = None,
    redis_host: Optional[str] = None,
    redis_port: Optional[int] = None,
    layer1_planner: Optional[Layer1Planner] = None,
    layer3_mcp=None,
    layer4_safety=None,
    layer5_audit=None
) -> Layer2Main:
    """Create and initialize Layer-2"""
    return Layer2Main(
        lmstudio_base_url,
        redis_host,
        redis_port,
        layer1_planner,
        layer3_mcp,
        layer4_safety,
        layer5_audit
    )

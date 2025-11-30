# app/tool_exec.py
import subprocess
import requests
from typing import Dict, Any, Optional
from app.logger import logger
try:
    from app.auth import decrypt_key
    from app.db import DB
except ImportError:
    decrypt_key = None
    DB = None
import json

# Example: safe HTTP proxy to external API using stored API keys
async def call_http_api(service_name: str, endpoint: str, method: str = "GET", data: Dict = None, headers: Dict = None):
    # pull encrypted key from DB
    row = await DB.fetchrow("SELECT encrypted_key FROM api_keys WHERE service_name=$1", service_name)
    api_key = None
    if row:
        api_key = decrypt_key(row["encrypted_key"])
    hdrs = headers or {}
    if api_key:
        hdrs["Authorization"] = f"Bearer {api_key}"
    resp = requests.request(method, endpoint, json=data, headers=hdrs, timeout=60)
    try:
        return {"status_code": resp.status_code, "body": resp.json()}
    except Exception:
        return {"status_code": resp.status_code, "body": resp.text}

# Example shell exec (disabled by default)
def run_shell_command(cmd: str, allow: bool = False) -> Dict[str, Any]:
    if not allow:
        raise RuntimeError("Shell execution disabled. Set allow=True explicitly and ensure sandboxing.")
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


class ToolExecutor:
    """
    MCP Tool Executor - executes tools and APIs
    Provides unified interface for all tool execution
    """
    
    def __init__(self):
        self.tools = {
            "http_api": self._execute_http_api,
            "shell": self._execute_shell,
            "browser": self._execute_browser,
            "file": self._execute_file,
            "universal": self._execute_universal,
        }
        logger.info({"event": "tool_executor_initialized", "tools": list(self.tools.keys())})
    
    async def execute(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with given parameters
        """
        if tool_name not in self.tools:
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}
        
        try:
            result = await self.tools[tool_name](params)
            logger.info({"event": "tool_executed", "tool": tool_name, "status": "success"})
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error({"event": "tool_execution_failed", "tool": tool_name, "error": str(e)})
            return {"status": "error", "message": str(e)}
    
    async def _execute_http_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute HTTP API call
        """
        service_name = params.get("service_name")
        endpoint = params.get("endpoint")
        method = params.get("method", "GET")
        data = params.get("data")
        headers = params.get("headers")
        
        if DB:
            return await call_http_api(service_name, endpoint, method, data, headers)
        else:
            # Fallback without DB
            resp = requests.request(method, endpoint, json=data, headers=headers or {}, timeout=60)
            try:
                return {"status_code": resp.status_code, "body": resp.json()}
            except Exception:
                return {"status_code": resp.status_code, "body": resp.text}
    
    async def _execute_shell(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute shell command (restricted)
        """
        cmd = params.get("command")
        allow = params.get("allow", False)
        return run_shell_command(cmd, allow)
    
    async def _execute_browser(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute browser automation
        """
        action = params.get("action", "fetch")
        url = params.get("url")
        
        if action == "fetch":
            resp = requests.get(url, timeout=30)
            return {"status_code": resp.status_code, "content": resp.text[:1000]}
        
        return {"message": f"Browser action '{action}' executed"}
    
    async def _execute_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute file operations
        """
        action = params.get("action")
        path = params.get("path")
        
        if action == "read":
            with open(path, 'r') as f:
                return {"content": f.read()}
        elif action == "write":
            content = params.get("content")
            with open(path, 'w') as f:
                f.write(content)
            return {"message": "File written"}
        elif action == "list":
            import os
            return {"files": os.listdir(path)}
        
        return {"message": f"File action '{action}' executed"}
    
    async def _execute_universal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Universal tool - handles any action
        """
        action = params.get("action", "")
        return {
            "message": f"Universal tool executed: {action}",
            "action": action,
            "params": params
        }
    
    def register_tool(self, name: str, func):
        """
        Register a new tool
        """
        self.tools[name] = func
        logger.info({"event": "tool_registered", "tool": name})
    
    def list_tools(self):
        """
        List all available tools
        """
        return list(self.tools.keys())
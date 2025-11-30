"""Sandboxed execution environment for Layer-4"""
import subprocess
from typing import Dict, Any, Optional


class SandboxRunner:
    """Execute commands in isolated sandbox"""
    
    def __init__(self, sandbox_type: str = "subprocess"):
        self.sandbox_type = sandbox_type
    
    def execute(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command in sandbox"""
        if self.sandbox_type == "subprocess":
            return self._subprocess_exec(command, context)
        elif self.sandbox_type == "docker":
            return self._docker_exec(command, context)
        else:
            return {"success": False, "error": f"Unknown sandbox type: {self.sandbox_type}"}
    
    def _subprocess_exec(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute in subprocess with timeout"""
        try:
            timeout = context.get("timeout", 30)
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _docker_exec(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute in Docker container"""
        container = context.get("container", "alpine:latest")
        docker_cmd = f"docker run --rm {container} sh -c '{command}'"
        return self._subprocess_exec(docker_cmd, context)

"""Capability-Based Access Control (CBAC) engine"""
import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class CBACEngine:
    """Manages agent capabilities and permissions"""
    
    def __init__(self, cbac_file: Optional[str] = None):
        self.cbac_file = Path(cbac_file) if cbac_file else Path(__file__).parent / "cbac.json"
        self.capabilities = self._load_capabilities()
    
    def _load_capabilities(self) -> Dict[str, Any]:
        """Load CBAC configuration"""
        if self.cbac_file.exists():
            return json.loads(self.cbac_file.read_text())
        return {
            "agents": {
                "DevOpsAgent": {
                    "capabilities": ["read_files", "write_files", "execute_safe_commands"],
                    "forbidden": ["delete_system_files", "format_disk"]
                },
                "SmartHomeAgent": {
                    "capabilities": ["control_lights", "control_thermostat"],
                    "forbidden": ["access_camera_without_approval"]
                },
                "BackupAgent": {
                    "capabilities": ["read_files", "write_backups"],
                    "forbidden": ["delete_files"]
                }
            }
        }
    
    def check_capability(self, agent_type: str, action: str) -> Dict[str, Any]:
        """Check if agent has capability for action"""
        agent_caps = self.capabilities.get("agents", {}).get(agent_type, {})
        
        if not agent_caps:
            return {"allowed": False, "reason": f"Unknown agent type: {agent_type}"}
        
        action_lower = action.lower()
        
        # Check for dangerous delete commands - BLOCK immediately
        dangerous_keywords = ['delete', 'remove', 'rm ', 'del ', 'unlink', 'drop', 'truncate', 'format']
        if any(keyword in action_lower for keyword in dangerous_keywords):
            return {"allowed": False, "reason": "Dangerous delete command blocked", "requires_approval": False}
        
        # Check forbidden actions
        forbidden = agent_caps.get("forbidden", [])
        if any(f in action_lower for f in forbidden):
            return {"allowed": False, "reason": f"Action forbidden for {agent_type}", "requires_approval": False}
        
        # Check for commands that need approval
        approval_keywords = ['install', 'update', 'upgrade', 'modify', 'change', 'set', 'configure']
        if any(keyword in action_lower for keyword in approval_keywords):
            return {"allowed": False, "reason": "Action requires approval", "requires_approval": True}
        
        # Check capabilities
        capabilities = agent_caps.get("capabilities", [])
        if not capabilities:
            return {"allowed": True, "reason": "No capability restrictions"}
        
        # Default allow for safe/read-only actions
        safe_keywords = ['list', 'read', 'check', 'get', 'show', 'display', 'view', 'open', 
                        'tell', 'fetch', 'news', 'latest', 'status', 'info', 'echo', 'launch', 'start']
        if any(keyword in action_lower for keyword in safe_keywords):
            return {"allowed": True, "reason": "Safe action allowed"}
        
        # Check if action contains any capability keyword
        for cap in capabilities:
            cap_lower = cap.lower()
            if cap_lower in action_lower or action_lower in cap_lower:
                return {"allowed": True, "reason": "Capability check passed"}
        
        return {"allowed": False, "reason": f"Action not in {agent_type} capabilities"}
    
    def add_capability(self, agent_type: str, capability: str):
        """Add new capability to agent"""
        if agent_type not in self.capabilities.get("agents", {}):
            self.capabilities.setdefault("agents", {})[agent_type] = {"capabilities": [], "forbidden": []}
        self.capabilities["agents"][agent_type]["capabilities"].append(capability)
        self._save_capabilities()
    
    def _save_capabilities(self):
        """Save capabilities to file"""
        self.cbac_file.parent.mkdir(parents=True, exist_ok=True)
        self.cbac_file.write_text(json.dumps(self.capabilities, indent=2))

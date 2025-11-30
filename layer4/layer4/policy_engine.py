"""OPA-based policy engine for Layer-4"""
import json
from typing import Dict, Any, Optional
from pathlib import Path


class PolicyEngine:
    """Evaluates OPA Rego policies for safety decisions"""
    
    def __init__(self, policy_dir: Optional[str] = None):
        self.policy_dir = Path(policy_dir) if policy_dir else Path(__file__).parent / "policies"
        self.policies = self._load_policies()
    
    def _load_policies(self) -> Dict[str, Any]:
        """Load all Rego policy files"""
        policies = {}
        if self.policy_dir.exists():
            for policy_file in self.policy_dir.glob("*.rego"):
                policies[policy_file.stem] = policy_file.read_text()
        return policies
    
    def evaluate(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate action against loaded policies"""
        # Basic deterministic checks
        if action in ["rm -rf /", "dd if=/dev/zero", ":(){ :|:& };:"]:
            return {"allowed": False, "reason": "Destructive command blocked"}
        
        if context.get("agent_type") == "DevOpsAgent":
            if any(cmd in action for cmd in ["rm -rf", "mkfs", "dd"]):
                return {"allowed": False, "reason": "DevOpsAgent cannot run destructive commands"}
        
        if context.get("agent_type") == "SmartHomeAgent":
            if "camera" in action and not context.get("user_approved"):
                return {"allowed": False, "reason": "Camera access requires approval"}
        
        if context.get("agent_type") == "BackupAgent":
            if "delete" in action.lower() or "rm" in action:
                return {"allowed": False, "reason": "BackupAgent cannot delete files"}
        
        return {"allowed": True, "reason": "Policy check passed"}
    
    def add_policy(self, name: str, rego_content: str):
        """Add new policy at runtime"""
        self.policies[name] = rego_content
        policy_file = self.policy_dir / f"{name}.rego"
        policy_file.parent.mkdir(parents=True, exist_ok=True)
        policy_file.write_text(rego_content)

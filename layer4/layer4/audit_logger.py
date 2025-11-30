"""Audit logging for Layer-4 safety decisions"""
import json
from typing import Dict, Any
from datetime import datetime
from pathlib import Path


class AuditLogger:
    """Logs all safety decisions and actions"""
    
    def __init__(self, log_file: str = "layer4_audit.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_decision(self, action: str, context: Dict[str, Any], decision: Dict[str, Any]):
        """Log safety decision"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "context": context,
            "decision": decision,
            "type": "safety_decision"
        }
        self._write_log(entry)
    
    def log_execution(self, action: str, result: Dict[str, Any]):
        """Log command execution"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "result": result,
            "type": "execution"
        }
        self._write_log(entry)
    
    def log_approval(self, approval_id: str, action: str, approved: bool):
        """Log approval decision"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "approval_id": approval_id,
            "action": action,
            "approved": approved,
            "type": "approval"
        }
        self._write_log(entry)
    
    def _write_log(self, entry: Dict[str, Any]):
        """Write log entry to file"""
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def get_logs(self, limit: int = 100) -> list:
        """Retrieve recent logs"""
        if not self.log_file.exists():
            return []
        
        logs = []
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return logs[-limit:]

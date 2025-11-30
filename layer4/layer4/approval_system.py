"""Human-in-the-loop approval system"""
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime


class ApprovalSystem:
    """Manages human approval for high-risk actions"""
    
    def __init__(self):
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self.approval_callback: Optional[Callable] = None
    
    async def request_approval(self, action: str, context: Dict[str, Any], timeout: int = 300) -> Dict[str, Any]:
        """Request human approval for action"""
        approval_id = f"approval_{datetime.utcnow().timestamp()}"
        
        self.pending_approvals[approval_id] = {
            "action": action,
            "context": context,
            "status": "pending",
            "requested_at": datetime.utcnow().isoformat()
        }
        
        # Notify approval system (WebSocket, CLI, UI)
        if self.approval_callback:
            await self.approval_callback(approval_id, action, context)
        
        # Wait for approval with timeout
        try:
            result = await asyncio.wait_for(
                self._wait_for_decision(approval_id),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            self.pending_approvals[approval_id]["status"] = "timeout"
            return {"approved": False, "reason": "Approval timeout"}
    
    async def _wait_for_decision(self, approval_id: str) -> Dict[str, Any]:
        """Wait for approval decision"""
        while True:
            approval = self.pending_approvals.get(approval_id, {})
            status = approval.get("status")
            
            if status == "approved":
                return {"approved": True, "reason": "User approved"}
            elif status == "rejected":
                return {"approved": False, "reason": "User rejected"}
            
            await asyncio.sleep(1)
    
    def approve(self, approval_id: str):
        """Approve pending action"""
        if approval_id in self.pending_approvals:
            self.pending_approvals[approval_id]["status"] = "approved"
    
    def reject(self, approval_id: str):
        """Reject pending action"""
        if approval_id in self.pending_approvals:
            self.pending_approvals[approval_id]["status"] = "rejected"
    
    def set_callback(self, callback: Callable):
        """Set callback for approval notifications"""
        self.approval_callback = callback

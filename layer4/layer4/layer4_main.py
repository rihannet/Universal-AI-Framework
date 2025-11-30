"""Layer-4 Main: Safety & Governance Orchestrator"""
import asyncio
from typing import Dict, Any, Optional
from .policy_engine import PolicyEngine
from .cbac_engine import CBACEngine
from .sandbox_runner import SandboxRunner
from .approval_system import ApprovalSystem
from .audit_logger import AuditLogger


class Layer4Main:
    """Main orchestrator for Layer-4 Safety & Governance"""
    
    def __init__(
        self,
        policy_dir: Optional[str] = None,
        cbac_file: Optional[str] = None,
        sandbox_type: str = "subprocess",
        audit_log: str = "layer4_audit.log",
        layer5_audit=None
    ):
        # Initialize all engines
        self.policy_engine = PolicyEngine(policy_dir)
        self.cbac_engine = CBACEngine(cbac_file)
        self.sandbox_runner = SandboxRunner(sandbox_type)
        self.approval_system = ApprovalSystem()
        self.audit_logger = AuditLogger(audit_log)
        self.layer5_audit = layer5_audit
        
        print("[Layer-4] Safety & Governance initialized")
        print(f"[Layer-4] Policies loaded: {len(self.policy_engine.policies)}")
        print(f"[Layer-4] CBAC agents: {len(self.cbac_engine.capabilities.get('agents', {}))}")
    
    async def validate_action(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate action through all safety checks"""
        agent_type = context.get("agent_type", "unknown")
        
        # Step 1: Policy check
        policy_result = self.policy_engine.evaluate(action, context)
        if not policy_result["allowed"]:
            self.audit_logger.log_decision(action, context, policy_result)
            return {"allowed": False, "reason": policy_result["reason"], "stage": "policy"}
        
        # Step 2: CBAC check
        cbac_result = self.cbac_engine.check_capability(agent_type, action)
        
        # If requires approval, ask user with Layer-5 verification
        if cbac_result.get("requires_approval"):
            print(f"\n[APPROVAL REQUIRED] Action: {action}")
            print(f"[APPROVAL REQUIRED] Reason: {cbac_result['reason']}")
            
            # Step 1: Ask for wallet signature (Layer-5 Web3 verification)
            if self.layer5_audit:
                print("\n[LAYER-5 VERIFICATION] Wallet authentication required")
                wallet_address = input("[LAYER-5] Enter wallet address: ").strip()
                signature = input("[LAYER-5] Enter signature: ").strip()
                
                # Verify signature via Layer-5
                try:
                    verified = self.layer5_audit.wallet_auth.verify_signature(
                        wallet_address,
                        signature,
                        action
                    )
                    
                    if not verified:
                        print("[LAYER-5] ❌ Wallet verification FAILED")
                        self.audit_logger.log_approval(f"approval_{action}", action, False)
                        return {"allowed": False, "reason": "Wallet verification failed", "stage": "layer5_verification"}
                    
                    print("[LAYER-5] ✅ Wallet verified")
                except Exception as e:
                    print(f"[LAYER-5] ⚠️ Verification skipped (mock mode): {e}")
            
            # Step 2: Ask for final approval
            user_input = input("[APPROVAL REQUIRED] Allow this action? (yes/no): ").strip().lower()
            
            if user_input == 'yes':
                self.audit_logger.log_approval(f"approval_{action}", action, True)
                print("[APPROVAL] ✅ Action approved by user")
                
                # Log to Layer-5 blockchain
                if self.layer5_audit:
                    try:
                        await self.layer5_audit.log_layer_action(
                            "Layer-4",
                            f"approval_granted:{action}",
                            {"action": action, "approved": True},
                            wallet_address if 'wallet_address' in locals() else "unknown"
                        )
                        print("[LAYER-5] ✅ Approval logged to blockchain")
                    except:
                        pass
            else:
                self.audit_logger.log_approval(f"approval_{action}", action, False)
                print("[APPROVAL] ❌ Action denied by user")
                return {"allowed": False, "reason": "User denied approval", "stage": "approval"}
        
        # If not allowed and not requiring approval, block
        elif not cbac_result["allowed"]:
            self.audit_logger.log_decision(action, context, cbac_result)
            return {"allowed": False, "reason": cbac_result["reason"], "stage": "cbac"}
        
        # All checks passed
        decision = {"allowed": True, "reason": "All safety checks passed"}
        self.audit_logger.log_decision(action, context, decision)
        return decision
    
    async def execute_safe(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and execute action safely"""
        # Validate first
        validation = await self.validate_action(action, context)
        if not validation["allowed"]:
            return {"success": False, "error": validation["reason"], "stage": validation.get("stage")}
        
        # Execute in sandbox
        result = self.sandbox_runner.execute(action, context)
        self.audit_logger.log_execution(action, result)
        
        return result
    
    def add_policy(self, name: str, rego_content: str):
        """Add new OPA policy"""
        self.policy_engine.add_policy(name, rego_content)
        print(f"[Layer-4] Policy added: {name}")
    
    def add_capability(self, agent_type: str, capability: str):
        """Add capability to agent"""
        self.cbac_engine.add_capability(agent_type, capability)
        print(f"[Layer-4] Capability added: {agent_type} -> {capability}")
    
    def get_audit_logs(self, limit: int = 100) -> list:
        """Retrieve audit logs"""
        return self.audit_logger.get_logs(limit)
    
    def set_approval_callback(self, callback):
        """Set callback for approval notifications"""
        self.approval_system.set_callback(callback)


# Convenience function for quick initialization
def create_layer4(
    policy_dir: Optional[str] = None,
    cbac_file: Optional[str] = None,
    sandbox_type: str = "subprocess",
    layer5_audit=None
) -> Layer4Main:
    """Create and initialize Layer-4"""
    return Layer4Main(policy_dir, cbac_file, sandbox_type, layer5_audit=layer5_audit)


# Example usage
if __name__ == "__main__":
    async def test_layer4():
        # Initialize Layer-4
        layer4 = create_layer4()
        
        # Test 1: Safe action
        result = await layer4.execute_safe(
            "echo 'Hello World'",
            {"agent_type": "DevOpsAgent"}
        )
        print(f"Test 1 (safe): {result}")
        
        # Test 2: Blocked action
        result = await layer4.execute_safe(
            "rm -rf /",
            {"agent_type": "DevOpsAgent"}
        )
        print(f"Test 2 (blocked): {result}")
        
        # Test 3: CBAC check
        result = await layer4.validate_action(
            "delete_files",
            {"agent_type": "BackupAgent"}
        )
        print(f"Test 3 (CBAC): {result}")
        
        # Test 4: Add new policy
        layer4.add_policy("custom", "package custom\ndefault allow = false")
        
        # Test 5: Get audit logs
        logs = layer4.get_audit_logs(limit=5)
        print(f"Test 5 (logs): {len(logs)} entries")
    
    asyncio.run(test_layer4())

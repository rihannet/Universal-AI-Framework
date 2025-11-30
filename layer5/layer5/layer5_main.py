"""Layer-5 Main: Web3 Identity & Decentralized Audit Orchestrator"""
import json
from typing import Dict, Any, Optional
from .services.ipfs_client import IPFSClient
from .services.blockchain_client import BlockchainClient
from .services.wallet_auth import WalletAuth
from .services.audit_store import AuditStore


class Layer5Main:
    """Main orchestrator for Layer-5 Web3 Identity & Audit"""
    
    def __init__(self):
        # Initialize all services
        self.ipfs = IPFSClient()
        self.blockchain = BlockchainClient()
        self.wallet_auth = WalletAuth()
        self.audit_store = AuditStore()
        
        print("[Layer-5] Web3 Identity & Audit initialized")
        print("[Layer-5] IPFS client ready")
        print("[Layer-5] Blockchain client ready")
        print("[Layer-5] Wallet auth ready")
        print("[Layer-5] Audit store ready")
    
    # Authentication methods
    def create_auth_challenge(self, wallet_address: str) -> Dict[str, Any]:
        """Create authentication challenge for wallet"""
        return self.wallet_auth.create_challenge(wallet_address)
    
    def verify_wallet_signature(self, nonce: str, signature: str, address: str) -> Dict[str, Any]:
        """Verify wallet signature and create session"""
        return self.wallet_auth.verify_signature(nonce, signature, address)
    
    def verify_session(self, token: str) -> Optional[str]:
        """Verify session token, return wallet address"""
        return self.wallet_auth.verify_token(token)
    
    # Audit log methods
    def upload_and_anchor(
        self,
        data: bytes,
        owner: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Upload to IPFS, anchor on blockchain, store in audit log"""
        # Step 1: Upload to IPFS
        ipfs_result = self.ipfs.upload(data)
        cid = ipfs_result["cid"]
        sha256_hash = ipfs_result["sha256"]
        
        # Step 2: Store in audit log
        audit = self.audit_store.store_audit(owner, cid, sha256_hash, metadata)
        
        # Step 3: Anchor on blockchain
        anchor_result = self.blockchain.anchor_hash(sha256_hash, owner)
        
        if anchor_result["success"]:
            self.audit_store.update_anchor_info(
                audit["id"],
                anchor_result["tx_hash"],
                anchor_result["block_number"]
            )
        
        return {
            "audit_id": audit["id"],
            "ipfs_cid": cid,
            "sha256": sha256_hash,
            "anchored": anchor_result["success"],
            "tx_hash": anchor_result.get("tx_hash"),
            "block_number": anchor_result.get("block_number")
        }
    
    def verify_audit(self, audit_id: int) -> Dict[str, Any]:
        """Verify audit log integrity"""
        audit = self.audit_store.get_audit(audit_id)
        
        if not audit:
            return {"valid": False, "error": "Audit not found"}
        
        # Verify IPFS hash
        ipfs_valid = self.ipfs.verify_hash(audit["ipfs_cid"], audit["sha256"])
        
        # Verify blockchain anchor
        blockchain_valid = False
        anchor_info = None
        
        if audit["anchored"]:
            anchor_info = self.blockchain.get_anchor(audit["sha256"])
            blockchain_valid = anchor_info is not None
        
        return {
            "valid": ipfs_valid and (not audit["anchored"] or blockchain_valid),
            "audit": audit,
            "ipfs_valid": ipfs_valid,
            "blockchain_valid": blockchain_valid,
            "anchor_info": anchor_info
        }
    
    def get_audit(self, audit_id: int) -> Optional[Dict[str, Any]]:
        """Get audit by ID"""
        return self.audit_store.get_audit(audit_id)
    
    def get_audits_by_owner(self, owner: str) -> list:
        """Get all audits for owner"""
        return self.audit_store.get_audits_by_owner(owner)
    
    def retrieve_audit_data(self, audit_id: int) -> Optional[bytes]:
        """Retrieve original data from IPFS"""
        audit = self.audit_store.get_audit(audit_id)
        if not audit:
            return None
        return self.ipfs.retrieve(audit["ipfs_cid"])
    
    # Integration methods for other layers
    def log_layer_action(
        self,
        layer: str,
        action: str,
        details: Dict[str, Any],
        owner: str = "system"
    ) -> Dict[str, Any]:
        """Log action from other layers (Layer-1, Layer-2, Layer-3, Layer-4)"""
        log_data = {
            "layer": layer,
            "action": action,
            "details": details
        }
        
        data_bytes = json.dumps(log_data, indent=2).encode()
        return self.upload_and_anchor(data_bytes, owner, {"type": "layer_action"})
    
    def verify_layer_action(self, audit_id: int) -> Dict[str, Any]:
        """Verify logged layer action"""
        verification = self.verify_audit(audit_id)
        
        if verification["valid"]:
            data = self.retrieve_audit_data(audit_id)
            if data:
                verification["action_data"] = json.loads(data.decode())
        
        return verification


# Convenience function
def create_layer5() -> Layer5Main:
    """Create and initialize Layer-5"""
    return Layer5Main()


# Example usage
if __name__ == "__main__":
    # Initialize Layer-5
    layer5 = create_layer5()
    
    print("\n" + "=" * 60)
    print("Layer-5 Demo")
    print("=" * 60)
    
    # Test 1: Wallet authentication
    print("\n[TEST 1] Wallet authentication...")
    wallet = "0x1234567890abcdef1234567890abcdef12345678"
    challenge = layer5.create_auth_challenge(wallet)
    print(f"Challenge created: {challenge['nonce'][:16]}...")
    
    # Simulate signature
    auth_result = layer5.verify_wallet_signature(
        challenge["nonce"],
        "0x" + "a" * 130,  # Mock signature
        wallet
    )
    print(f"Auth result: {auth_result['success']}")
    
    if auth_result["success"]:
        token = auth_result["token"]
        verified_address = layer5.verify_session(token)
        print(f"Session verified: {verified_address}")
    
    # Test 2: Upload and anchor audit log
    print("\n[TEST 2] Upload and anchor audit log...")
    audit_data = b"Critical system action: User login at 2024-01-01"
    result = layer5.upload_and_anchor(audit_data, wallet, {"type": "login"})
    print(f"Audit ID: {result['audit_id']}")
    print(f"IPFS CID: {result['ipfs_cid']}")
    print(f"SHA256: {result['sha256'][:16]}...")
    print(f"Anchored: {result['anchored']}")
    print(f"TX Hash: {result['tx_hash']}")
    
    # Test 3: Verify audit
    print("\n[TEST 3] Verify audit...")
    verification = layer5.verify_audit(result["audit_id"])
    print(f"Valid: {verification['valid']}")
    print(f"IPFS valid: {verification['ipfs_valid']}")
    print(f"Blockchain valid: {verification['blockchain_valid']}")
    
    # Test 4: Log layer action
    print("\n[TEST 4] Log layer action...")
    layer_log = layer5.log_layer_action(
        "Layer-4",
        "policy_check",
        {"agent": "DevOpsAgent", "action": "rm -rf /", "blocked": True},
        wallet
    )
    print(f"Layer action logged: {layer_log['audit_id']}")
    
    # Test 5: Verify layer action
    print("\n[TEST 5] Verify layer action...")
    layer_verification = layer5.verify_layer_action(layer_log["audit_id"])
    print(f"Valid: {layer_verification['valid']}")
    print(f"Action: {layer_verification['action_data']['action']}")
    
    # Test 6: Get audits by owner
    print("\n[TEST 6] Get audits by owner...")
    audits = layer5.get_audits_by_owner(wallet)
    print(f"Total audits: {len(audits)}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

"""Blockchain client for on-chain anchoring"""
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime


class BlockchainClient:
    """Simple blockchain client (mock for local testing)"""
    
    def __init__(self):
        self.anchors = {}  # Mock blockchain storage
        self.block_number = 0
    
    def anchor_hash(self, sha256_hash: str, submitter: str = "system") -> Dict[str, Any]:
        """Anchor hash on blockchain"""
        if sha256_hash in self.anchors:
            return {"success": False, "error": "Hash already anchored"}
        
        self.block_number += 1
        tx_hash = f"0x{hashlib.sha256(f'{sha256_hash}{self.block_number}'.encode()).hexdigest()}"
        
        self.anchors[sha256_hash] = {
            "hash": sha256_hash,
            "submitter": submitter,
            "timestamp": datetime.utcnow().isoformat(),
            "block_number": self.block_number,
            "tx_hash": tx_hash
        }
        
        return {
            "success": True,
            "tx_hash": tx_hash,
            "block_number": self.block_number
        }
    
    def get_anchor(self, sha256_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve anchor info from blockchain"""
        return self.anchors.get(sha256_hash)
    
    def verify_anchor(self, sha256_hash: str) -> bool:
        """Verify if hash is anchored"""
        return sha256_hash in self.anchors

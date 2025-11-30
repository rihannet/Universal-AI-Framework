"""IPFS client for off-chain storage"""
import hashlib
import json
from typing import Dict, Any


class IPFSClient:
    """Simple IPFS client (mock for local testing, replace with real IPFS)"""
    
    def __init__(self):
        self.storage = {}  # Mock storage
    
    def upload(self, data: bytes) -> Dict[str, Any]:
        """Upload data to IPFS, return CID and hash"""
        sha256_hash = hashlib.sha256(data).hexdigest()
        cid = f"Qm{sha256_hash[:44]}"  # Mock CID
        
        self.storage[cid] = data
        
        return {
            "cid": cid,
            "sha256": sha256_hash,
            "size": len(data)
        }
    
    def retrieve(self, cid: str) -> bytes:
        """Retrieve data from IPFS by CID"""
        return self.storage.get(cid, b"")
    
    def verify_hash(self, cid: str, expected_hash: str) -> bool:
        """Verify data integrity"""
        data = self.retrieve(cid)
        if not data:
            return False
        actual_hash = hashlib.sha256(data).hexdigest()
        return actual_hash == expected_hash

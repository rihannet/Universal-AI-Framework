"""Audit log storage"""
from typing import Dict, Any, List, Optional
from datetime import datetime


class AuditStore:
    """In-memory audit log storage (replace with DB in production)"""
    
    def __init__(self):
        self.audits = {}
        self.next_id = 1
    
    def store_audit(
        self,
        owner: str,
        ipfs_cid: str,
        sha256_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Store audit log entry"""
        audit_id = self.next_id
        self.next_id += 1
        
        audit = {
            "id": audit_id,
            "owner": owner,
            "ipfs_cid": ipfs_cid,
            "sha256": sha256_hash,
            "metadata": metadata or {},
            "anchored": False,
            "anchor_tx": None,
            "anchor_block": None,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.audits[audit_id] = audit
        return audit
    
    def update_anchor_info(self, audit_id: int, tx_hash: str, block_number: int):
        """Update audit with anchor information"""
        if audit_id in self.audits:
            self.audits[audit_id]["anchored"] = True
            self.audits[audit_id]["anchor_tx"] = tx_hash
            self.audits[audit_id]["anchor_block"] = block_number
    
    def get_audit(self, audit_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve audit by ID"""
        return self.audits.get(audit_id)
    
    def get_audits_by_owner(self, owner: str) -> List[Dict[str, Any]]:
        """Get all audits for owner"""
        return [a for a in self.audits.values() if a["owner"] == owner]
    
    def get_audit_by_hash(self, sha256_hash: str) -> Optional[Dict[str, Any]]:
        """Find audit by hash"""
        for audit in self.audits.values():
            if audit["sha256"] == sha256_hash:
                return audit
        return None

"""Wallet-based authentication"""
import hashlib
import secrets
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class WalletAuth:
    """Wallet-based authentication system"""
    
    def __init__(self):
        self.challenges = {}  # nonce -> {address, expires}
        self.sessions = {}    # token -> {address, expires}
    
    def create_challenge(self, address: str) -> Dict[str, Any]:
        """Create authentication challenge for wallet"""
        nonce = secrets.token_hex(32)
        expires = datetime.utcnow() + timedelta(minutes=5)
        
        self.challenges[nonce] = {
            "address": address,
            "expires": expires
        }
        
        return {
            "nonce": nonce,
            "message": f"Sign this message to authenticate: {nonce}",
            "expires_at": expires.isoformat()
        }
    
    def verify_signature(self, nonce: str, signature: str, address: str) -> Dict[str, Any]:
        """Verify wallet signature (simplified)"""
        challenge = self.challenges.get(nonce)
        
        if not challenge:
            return {"success": False, "error": "Invalid nonce"}
        
        if datetime.utcnow() > challenge["expires"]:
            del self.challenges[nonce]
            return {"success": False, "error": "Challenge expired"}
        
        if challenge["address"].lower() != address.lower():
            return {"success": False, "error": "Address mismatch"}
        
        # Simplified verification (in production, use eth_account.recover_message)
        if len(signature) < 10:
            return {"success": False, "error": "Invalid signature"}
        
        # Create session token
        token = secrets.token_hex(32)
        self.sessions[token] = {
            "address": address,
            "expires": datetime.utcnow() + timedelta(hours=24)
        }
        
        del self.challenges[nonce]
        
        return {
            "success": True,
            "token": token,
            "address": address
        }
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify session token, return address if valid"""
        session = self.sessions.get(token)
        
        if not session:
            return None
        
        if datetime.utcnow() > session["expires"]:
            del self.sessions[token]
            return None
        
        return session["address"]

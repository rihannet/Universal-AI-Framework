# app/auth.py
import os
import time
from typing import Dict
from jose import jwt
from cryptography.fernet import Fernet

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_SECONDS = int(os.getenv("JWT_EXP_SECONDS", "3600"))
FERNET_KEY = os.getenv("FERNET_KEY")

fernet = Fernet(FERNET_KEY.encode()) if FERNET_KEY else None

def create_token(claims: Dict[str, str], expires_in: int = None) -> str:
    exp = int(time.time()) + (expires_in or JWT_EXP_SECONDS)
    payload = {**claims, "exp": exp}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_token(token: str) -> Dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

def encrypt_key(plain: str) -> str:
    if not fernet:
        raise RuntimeError("FERNET_KEY not set")
    return fernet.encrypt(plain.encode()).decode()

def decrypt_key(enc: str) -> str:
    if not fernet:
        raise RuntimeError("FERNET_KEY not set")
    return fernet.decrypt(enc.encode()).decode()
import os
import hashlib
import secrets
import time
from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # .env'den okunur
TOKEN_SECRET = os.getenv("TOKEN_SECRET", secrets.token_hex(32))
TOKEN_EXPIRY = 24 * 60 * 60  # 24 saat

# Basit token store (in-memory, restart'ta token'lar geçersiz olur - tek sunucu için yeterli)
_active_tokens: dict[str, float] = {}

security = HTTPBearer()


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def login(password: str) -> Optional[str]:
    """Şifre doğruysa token döndürür, yanlışsa None."""
    if _hash_password(password) == _hash_password(ADMIN_PASSWORD):
        token = secrets.token_urlsafe(48)
        _active_tokens[token] = time.time() + TOKEN_EXPIRY
        return token
    return None


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """FastAPI dependency: Bearer token doğrulama."""
    token = credentials.credentials
    expiry = _active_tokens.get(token)

    if expiry is None:
        raise HTTPException(status_code=401, detail="Geçersiz token")

    if time.time() > expiry:
        _active_tokens.pop(token, None)
        raise HTTPException(status_code=401, detail="Token süresi dolmuş")

    return True


def logout(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """Token'ı geçersiz kılır."""
    token = credentials.credentials
    _active_tokens.pop(token, None)
    return True

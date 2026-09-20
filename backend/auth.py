from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import get_db
from models import User, RefreshToken, AuditLog, UserRole
from schemas import TokenData
import secrets
import hashlib

SECRET_KEY = "super-secret-key-for-letsfiohub-2026-production-ready"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "type": "refresh", "jti": secrets.token_hex(16)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str, expected_type: str = "access"):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type:
            return None
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return {"user_id": int(user_id), "payload": payload}
    except (JWTError, ValueError, TypeError):
        return None

def generate_verification_code() -> str:
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

def get_device_fingerprint(request: Request) -> str:
    user_agent = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else "unknown"
    fingerprint_data = f"{user_agent}:{ip}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:32]

def log_audit_event(db: Session, user_id: Optional[int], action: str, request: Request, details: str = None):
    log = AuditLog(
        user_id=user_id,
        action=action,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details=details
    )
    db.add(log)
    db.commit()

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    token = auth_header.split(" ", 1)[1]
    decoded = decode_token(token, "access")
    
    if decoded is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = db.query(User).filter(User.id == decoded["user_id"]).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    
    return user

def require_role(required_role: UserRole):
    async def role_checker(current_user: User = Depends(get_current_user)):
        role_hierarchy = {UserRole.USER: 0, UserRole.MODERATOR: 1, UserRole.ADMIN: 2}
        if role_hierarchy.get(current_user.role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return role_checker

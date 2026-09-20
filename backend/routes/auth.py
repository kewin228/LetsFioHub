from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from database import get_db
from models import User, RefreshToken, UserRole
from schemas import (
    UserCreate, UserLogin, TokenPair, TokenRefresh,
    PasswordReset, PasswordResetConfirm, VerifyEmail,
    UserResponse, UserProfileResponse, UserUpdate, AdminUserUpdate
)
from auth import (
    get_password_hash, verify_password, create_access_token, create_refresh_token,
    decode_access_token, generate_verification_code, get_device_fingerprint, log_audit,
    get_current_user, require_role, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS,
    MAX_LOGIN_ATTEMPTS, LOCKOUT_DURATION_MINUTES
)
from typing import List

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db), request: Request = None):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    verification_code = generate_verification_code()
    db_user = User(
        role=UserRole.USER,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        username=user.username,
        display_name=user.display_name or user.username,
        verification_code=verification_code,
        verification_code_expires=datetime.utcnow() + timedelta(minutes=30)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    log_audit(db, db_user.id, "REGISTER", request)
    print(f"Verification code for {user.email}: {verification_code}")
    return db_user

@router.post("/verify-email")
def verify_email(code: VerifyEmail, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), request: Request = None):
    if current_user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")
    if current_user.verification_code != code.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")
    if current_user.verification_code_expires < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code expired")
    current_user.is_verified = True
    current_user.verification_code = None
    current_user.verification_code_expires = None
    db.commit()
    log_audit(db, current_user.id, "EMAIL_VERIFIED", request)
    return {"message": "Email verified successfully"}

@router.post("/login", response_model=TokenPair)
def login(user_credentials: UserLogin, db: Session = Depends(get_db), request: Request = None):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if user and user.locked_until and user.locked_until > datetime.utcnow():
        minutes_left = int((user.locked_until - datetime.utcnow()).total_seconds() / 60)
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"Account locked. Try again in {minutes_left} minutes")
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                log_audit(db, user.id, "ACCOUNT_LOCKED", request, f"Locked after {MAX_LOGIN_ATTEMPTS} failed attempts")
            db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    db.commit()
    device_fp = get_device_fingerprint(request)
    access_token = create_access_token(data={"sub": user.id})
    refresh_token_obj = RefreshToken(
        token=create_refresh_token(data={"sub": user.id}),
        user_id=user.id,
        device_info=device_fp,
        ip_address=request.client.host if request.client else None,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(refresh_token_obj)
    db.commit()
    log_audit(db, user.id, "LOGIN", request, f"Device: {device_fp}")
    return {"access_token": access_token, "refresh_token": refresh_token_obj.token, "token_type": "bearer", "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60}

@router.post("/refresh", response_model=TokenPair)
def refresh_token(body: TokenRefresh, db: Session = Depends(get_db), request: Request = None):
    decoded = decode_access_token(body.refresh_token, "refresh")
    if decoded is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    db_token = db.query(RefreshToken).filter(RefreshToken.token == body.refresh_token, RefreshToken.is_revoked == False, RefreshToken.expires_at > datetime.utcnow()).first()
    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or revoked")
    user = db.query(User).filter(User.id == decoded["user_id"]).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    db_token.is_revoked = True
    db.commit()
    new_access_token = create_access_token(data={"sub": user.id})
    new_refresh_token = RefreshToken(token=create_refresh_token(data={"sub": user.id}), user_id=user.id, device_info=db_token.device_info, ip_address=request.client.host if request.client else None, expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    db.add(new_refresh_token)
    db.commit()
    return {"access_token": new_access_token, "refresh_token": new_refresh_token.token, "token_type": "bearer", "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60}

@router.post("/logout")
def logout(body: TokenRefresh, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), request: Request = None):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == body.refresh_token).first()
    if db_token:
        db_token.is_revoked = True
        db.commit()
    log_audit(db, current_user.id, "LOGOUT", request)
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(profile: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), request: Request = None):
    if profile.display_name is not None: current_user.display_name = profile.display_name
    if profile.bio is not None: current_user.bio = profile.bio
    if profile.avatar_url is not None: current_user.avatar_url = profile.avatar_url
    if profile.country is not None: current_user.country = profile.country
    db.commit()
    db.refresh(current_user)
    log_audit(db, current_user.id, "PROFILE_UPDATED", request)
    return current_user

@router.post("/forgot-password")
def forgot_password(body: PasswordReset, db: Session = Depends(get_db), request: Request = None):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        return {"message": "If email exists, reset link has been sent"}
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    print(f"Password reset token for {body.email}: {reset_token}")
    log_audit(db, user.id, "PASSWORD_RESET_REQUESTED", request)
    return {"message": "If email exists, reset link has been sent"}

@router.post("/reset-password")
def reset_password(body: PasswordResetConfirm, db: Session = Depends(get_db), request: Request = None):
    user = db.query(User).filter(User.reset_token == body.token, User.reset_token_expires > datetime.utcnow()).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    user.hashed_password = get_password_hash(body.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    log_audit(db, user.id, "PASSWORD_CHANGED", request)
    return {"message": "Password reset successfully"}

@router.get("/users", response_model=List[UserResponse])
def list_users(current_user: User = Depends(require_role(UserRole.ADMIN)), db: Session = Depends(get_db)):
    return db.query(User).all()

@router.patch("/users/{user_id}", response_model=UserResponse)
def admin_update_user(user_id: int, updates: AdminUserUpdate, current_user: User = Depends(require_role(UserRole.ADMIN)), db: Session = Depends(get_db), request: Request = None):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if updates.role is not None: user.role = updates.role
    if updates.is_active is not None: user.is_active = updates.is_active
    db.commit()
    db.refresh(user)
    log_audit(db, current_user.id, "ADMIN_USER_UPDATED", request, f"Updated user {user_id}")
    return user

@router.get("/audit-logs")
def get_audit_logs(current_user: User = Depends(require_role(UserRole.ADMIN)), db: Session = Depends(get_db)):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()

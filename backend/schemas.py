from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional, List
from models import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str
    display_name: Optional[str] = None
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900

class TokenRefresh(BaseModel):
    refresh_token: str

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class VerifyEmail(BaseModel):
    code: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    role: UserRole
    is_verified: bool
    created_at: datetime
    country: Optional[str]
    class Config:
        from_attributes = True

class UserProfileResponse(UserResponse):
    last_login: Optional[datetime]
    updated_at: Optional[datetime]

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    country: Optional[str] = None

class AdminUserUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class VideoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    thumbnail: Optional[str] = None
    style: str

class VideoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    url: str
    thumbnail: Optional[str]
    style: str
    views: int
    created_at: datetime
    user_id: Optional[int]
    class Config:
        from_attributes = True

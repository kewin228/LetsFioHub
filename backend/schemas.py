from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str
    display_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    is_verified: bool
    created_at: datetime
    country: Optional[str]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

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

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password: str = Column(String(255), nullable=False)
    username: str = Column(String(100), unique=True, index=True, nullable=False)
    display_name: str = Column(String(100), nullable=True)
    bio: str = Column(Text, nullable=True)
    avatar_url: str = Column(String(500), nullable=True)
    is_active: bool = Column(Boolean, default=True)
    is_verified: bool = Column(Boolean, default=False)
    created_at: DateTime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: DateTime = Column(DateTime(timezone=True), onupdate=func.now())
    last_login: DateTime = Column(DateTime(timezone=True), nullable=True)
    country: str = Column(String(100), nullable=True)
    birth_date: DateTime = Column(DateTime, nullable=True)

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    url = Column(String)  # YouTube URL или ссылка на видео
    thumbnail = Column(String, nullable=True)
    style = Column(String, index=True)  # Cyberpunk, Cod, Fortnite, etc.
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

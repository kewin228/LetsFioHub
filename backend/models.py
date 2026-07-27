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

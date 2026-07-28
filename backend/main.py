from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, get_db
from models import User
from auth import get_current_user

# Создаём таблицы
Base.metadata.create_all(bind=engine)

from routes.auth import router as auth_router

app = FastAPI(title="Let'sFioHub API")

# CORS middleware - ДОЛЖЕН БЫТЬ ПЕРВЫМ!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

@app.get("/")
def root():
    return {"message": "Let'sFioHub API is running"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "display_name": current_user.display_name,
        "bio": current_user.bio,
        "avatar_url": current_user.avatar_url,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
        "country": current_user.country,
    }

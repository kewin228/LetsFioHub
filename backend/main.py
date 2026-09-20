from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from models import User, Video

Base.metadata.create_all(bind=engine)

from routes.auth import router as auth_router
from routes.videos import router as videos_router

app = FastAPI(title="Let'sFioHub API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(videos_router, prefix="/api/videos", tags=["videos"])

@app.get("/")
def root():
    return {"message": "Let'sFioHub API v2.0", "docs": "/docs"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "2.0.0"}

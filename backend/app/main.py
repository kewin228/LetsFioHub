from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime

app = FastAPI(title="Let's FioHub API", version="2.0.0")

# Разрешаем CORS для всех источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все источники
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Временное хранилище видео
videos_db = []

@app.get("/")
def root():
    return {"message": "Let's FioHub API v2.0", "endpoints": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/v1/videos")
def get_videos():
    return {"videos": videos_db, "total": len(videos_db)}

@app.post("/api/v1/videos/upload")
async def upload_video(
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    user_id: int = 1
):
    video_id = str(uuid.uuid4())[:8]
    
    # Сохраняем информацию о видео
    new_video = {
        "id": video_id,
        "title": title,
        "description": description,
        "file_path": f"uploads/{video_id}.mp4",
        "views": 0,
        "likes": 0,
        "uploader_id": user_id,
        "created_at": datetime.now().isoformat()
    }
    videos_db.append(new_video)
    
    return {"message": "Video uploaded", "video_id": video_id}

@app.get("/api/v1/videos/{video_id}")
def get_video(video_id: str):
    for video in videos_db:
        if video["id"] == video_id:
            video["views"] += 1
            return video
    return JSONResponse(status_code=404, content={"error": "Video not found"})

@app.get("/api/v1/videos/{video_id}/stream")
def stream_video(video_id: str):
    return JSONResponse(status_code=501, content={"error": "Streaming not implemented yet"})

@app.post("/api/v1/videos/{video_id}/like")
def like_video(video_id: str, user_id: int = 1):
    for video in videos_db:
        if video["id"] == video_id:
            video["likes"] += 1
            return {"message": "Liked", "likes": video["likes"]}
    return JSONResponse(status_code=404, content={"error": "Video not found"})

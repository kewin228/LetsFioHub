from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid
from datetime import datetime

app = FastAPI(title="Let's FioHub API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем папки
os.makedirs("uploads/videos", exist_ok=True)
os.makedirs("uploads/thumbnails", exist_ok=True)

# ========== МОДЕЛИ ==========
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar: Optional[str] = None
    subscriber_count: int = 0

class VideoCreate(BaseModel):
    title: str
    description: str = ""
    is_public: bool = True

class VideoResponse(BaseModel):
    id: str
    title: str
    description: str
    file_path: str
    thumbnail_path: Optional[str] = None
    views: int = 0
    likes: int = 0
    dislikes: int = 0
    uploader_id: int
    created_at: str
    uploader: Optional[UserResponse] = None

class CommentCreate(BaseModel):
    text: str
    parent_id: Optional[int] = None

class PlaylistCreate(BaseModel):
    name: str
    description: str = ""
    is_public: bool = True

# ========== ХРАНИЛИЩА ==========
users_db = []
videos_db = []
comments_db = []
likes_db = []
subscriptions_db = []
playlists_db = []
playlist_videos_db = []
watch_history_db = []

current_user_id = 1
current_comment_id = 1
current_playlist_id = 1

# Создаем тестового пользователя
users_db.append({
    "id": 1,
    "username": "admin",
    "email": "admin@fiohub.com",
    "avatar": None,
    "subscriber_count": 0,
    "created_at": datetime.now().isoformat()
})

# ========== ПОЛЬЗОВАТЕЛИ ==========
@app.post("/api/v1/auth/register")
def register(user: UserCreate):
    global current_user_id
    for u in users_db:
        if u["email"] == user.email:
            return {"error": "Email already exists"}
    new_user = {
        "id": current_user_id,
        "username": user.username,
        "email": user.email,
        "avatar": None,
        "subscriber_count": 0,
        "created_at": datetime.now().isoformat()
    }
    users_db.append(new_user)
    current_user_id += 1
    return {"message": "User created", "user": new_user}

@app.post("/api/v1/auth/login")
def login(user: UserLogin):
    for u in users_db:
        if u["email"] == user.email:
            return {"message": "Login successful", "user": u}
    return {"error": "Invalid credentials"}

@app.get("/api/v1/users/{user_id}")
def get_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(404, "User not found")

@app.get("/api/v1/users/{user_id}/videos")
def get_user_videos(user_id: int):
    return [v for v in videos_db if v["uploader_id"] == user_id]

# ========== ПОДПИСКИ ==========
@app.post("/api/v1/users/{channel_id}/subscribe")
def subscribe(channel_id: int, subscriber_id: int = 1):
    for sub in subscriptions_db:
        if sub["subscriber_id"] == subscriber_id and sub["channel_id"] == channel_id:
            return {"message": "Already subscribed"}
    
    subscriptions_db.append({
        "subscriber_id": subscriber_id,
        "channel_id": channel_id,
        "created_at": datetime.now().isoformat()
    })
    
    for user in users_db:
        if user["id"] == channel_id:
            user["subscriber_count"] += 1
            break
    
    return {"message": "Subscribed", "subscribers": get_channel_subscribers(channel_id)}

@app.delete("/api/v1/users/{channel_id}/subscribe")
def unsubscribe(channel_id: int, subscriber_id: int = 1):
    global subscriptions_db
    subscriptions_db = [s for s in subscriptions_db if not (s["subscriber_id"] == subscriber_id and s["channel_id"] == channel_id)]
    
    for user in users_db:
        if user["id"] == channel_id:
            user["subscriber_count"] = max(0, user["subscriber_count"] - 1)
            break
    
    return {"message": "Unsubscribed"}

@app.get("/api/v1/users/{channel_id}/subscribers")
def get_subscribers(channel_id: int):
    count = sum(1 for s in subscriptions_db if s["channel_id"] == channel_id)
    return {"subscribers": count}

def get_channel_subscribers(channel_id: int):
    return sum(1 for s in subscriptions_db if s["channel_id"] == channel_id)

@app.get("/api/v1/users/me/subscriptions")
def get_subscriptions(subscriber_id: int = 1):
    subscribed_channels = []
    for sub in subscriptions_db:
        if sub["subscriber_id"] == subscriber_id:
            for user in users_db:
                if user["id"] == sub["channel_id"]:
                    subscribed_channels.append(user)
                    break
    return {"subscriptions": subscribed_channels}

# ========== ВИДЕО ==========
@app.post("/api/v1/videos/upload")
async def upload_video(
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    user_id: int = 1
):
    video_id = str(uuid.uuid4())[:8]
    file_path = f"uploads/videos/{video_id}.mp4"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    new_video = {
        "id": video_id,
        "title": title,
        "description": description,
        "file_path": file_path,
        "thumbnail_path": None,
        "views": 0,
        "likes": 0,
        "dislikes": 0,
        "uploader_id": user_id,
        "created_at": datetime.now().isoformat()
    }
    videos_db.append(new_video)
    
    return {"message": "Video uploaded", "video_id": video_id}

@app.get("/api/v1/videos")
def get_videos(limit: int = 20, offset: int = 0):
    result = []
    for video in sorted(videos_db, key=lambda x: x["created_at"], reverse=True)[offset:offset+limit]:
        video_copy = video.copy()
        for user in users_db:
            if user["id"] == video["uploader_id"]:
                video_copy["uploader"] = user
                break
        result.append(video_copy)
    return {"videos": result, "total": len(videos_db)}

@app.get("/api/v1/videos/recommendations")
def get_recommendations(user_id: int = 1, limit: int = 10):
    # Рекомендации на основе просмотров
    sorted_videos = sorted(videos_db, key=lambda x: x["views"], reverse=True)
    result = []
    for video in sorted_videos[:limit]:
        video_copy = video.copy()
        for user in users_db:
            if user["id"] == video["uploader_id"]:
                video_copy["uploader"] = user
                break
        result.append(video_copy)
    return {"recommendations": result}

@app.get("/api/v1/videos/trending")
def get_trending(limit: int = 10):
    # Трендовые видео (по лайкам)
    sorted_videos = sorted(videos_db, key=lambda x: x["likes"], reverse=True)
    result = []
    for video in sorted_videos[:limit]:
        video_copy = video.copy()
        for user in users_db:
            if user["id"] == video["uploader_id"]:
                video_copy["uploader"] = user
                break
        result.append(video_copy)
    return {"trending": result}

@app.get("/api/v1/videos/{video_id}")
def get_video(video_id: str, user_id: int = 1):
    for video in videos_db:
        if video["id"] == video_id:
            video["views"] += 1
            # Добавляем в историю
            watch_history_db.append({
                "user_id": user_id,
                "video_id": video_id,
                "watched_at": datetime.now().isoformat()
            })
            for user in users_db:
                if user["id"] == video["uploader_id"]:
                    video["uploader"] = user
                    break
            return video
    raise HTTPException(404, "Video not found")

@app.get("/api/v1/videos/{video_id}/stream")
def stream_video(video_id: str):
    for video in videos_db:
        if video["id"] == video_id:
            if os.path.exists(video["file_path"]):
                return FileResponse(video["file_path"], media_type="video/mp4")
    raise HTTPException(404, "Video not found")

@app.post("/api/v1/videos/{video_id}/like")
def like_video(video_id: str, user_id: int = 1):
    for video in videos_db:
        if video["id"] == video_id:
            video["likes"] += 1
            return {"message": "Liked", "likes": video["likes"]}
    raise HTTPException(404, "Video not found")

# ========== КОММЕНТАРИИ ==========
@app.post("/api/v1/videos/{video_id}/comments")
def create_comment(video_id: str, comment: CommentCreate, user_id: int = 1):
    global current_comment_id
    new_comment = {
        "id": current_comment_id,
        "text": comment.text,
        "video_id": video_id,
        "author_id": user_id,
        "likes": 0,
        "parent_id": comment.parent_id,
        "created_at": datetime.now().isoformat()
    }
    comments_db.append(new_comment)
    current_comment_id += 1
    
    for user in users_db:
        if user["id"] == user_id:
            new_comment["author"] = user
            break
    return new_comment

@app.get("/api/v1/videos/{video_id}/comments")
def get_comments(video_id: str):
    result = []
    for comment in comments_db:
        if comment["video_id"] == video_id and comment.get("parent_id") is None:
            comment_copy = comment.copy()
            for user in users_db:
                if user["id"] == comment["author_id"]:
                    comment_copy["author"] = user
                    break
            result.append(comment_copy)
    return sorted(result, key=lambda x: x["created_at"], reverse=True)

# ========== ПЛЕЙЛИСТЫ ==========
@app.post("/api/v1/playlists")
def create_playlist(playlist: PlaylistCreate, user_id: int = 1):
    global current_playlist_id
    new_playlist = {
        "id": current_playlist_id,
        "name": playlist.name,
        "description": playlist.description,
        "is_public": playlist.is_public,
        "user_id": user_id,
        "videos": [],
        "created_at": datetime.now().isoformat()
    }
    playlists_db.append(new_playlist)
    current_playlist_id += 1
    return new_playlist

@app.get("/api/v1/users/me/playlists")
def get_my_playlists(user_id: int = 1):
    return [p for p in playlists_db if p["user_id"] == user_id]

@app.post("/api/v1/playlists/{playlist_id}/videos/{video_id}")
def add_to_playlist(playlist_id: int, video_id: str):
    for playlist in playlists_db:
        if playlist["id"] == playlist_id:
            if video_id not in playlist["videos"]:
                playlist["videos"].append(video_id)
            return {"message": "Added to playlist"}
    raise HTTPException(404, "Playlist not found")

@app.get("/api/v1/playlists/{playlist_id}")
def get_playlist(playlist_id: int):
    for playlist in playlists_db:
        if playlist["id"] == playlist_id:
            playlist_copy = playlist.copy()
            playlist_copy["video_details"] = []
            for video_id in playlist["videos"]:
                for video in videos_db:
                    if video["id"] == video_id:
                        playlist_copy["video_details"].append(video)
                        break
            return playlist_copy
    raise HTTPException(404, "Playlist not found")

# ========== ПОИСК ==========
@app.get("/api/v1/search")
def search(q: str, type: str = "all"):
    results = {"videos": [], "channels": []}
    
    # Поиск видео
    if type in ["all", "videos"]:
        for video in videos_db:
            if q.lower() in video["title"].lower() or q.lower() in video["description"].lower():
                video_copy = video.copy()
                for user in users_db:
                    if user["id"] == video["uploader_id"]:
                        video_copy["uploader"] = user
                        break
                results["videos"].append(video_copy)
    
    # Поиск каналов
    if type in ["all", "channels"]:
        for user in users_db:
            if q.lower() in user["username"].lower():
                results["channels"].append(user)
    
    return results

# ========== ИСТОРИЯ ==========
@app.get("/api/v1/users/me/history")
def get_watch_history(user_id: int = 1, limit: int = 20):
    history = []
    for item in sorted(watch_history_db, key=lambda x: x["watched_at"], reverse=True)[:limit]:
        if item["user_id"] == user_id:
            for video in videos_db:
                if video["id"] == item["video_id"]:
                    history.append(video)
                    break
    return {"history": history}

# ========== HEALTH ==========
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "users": len(users_db),
        "videos": len(videos_db),
        "comments": len(comments_db),
        "playlists": len(playlists_db)
    }

@app.get("/")
def root():
    return {"message": "Let's FioHub API v2.0", "endpoints": "/docs"}

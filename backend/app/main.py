from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import FileResponse
import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os

SECRET_KEY = "your-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Let's FioHub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("sub"))
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- МОДЕЛИ ---
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class CommentCreate(BaseModel):
    text: str

class CommentResponse(BaseModel):
    id: int
    text: str
    author_id: int
    author_name: str
    created_at: str
    likes: int

# --- ХРАНИЛИЩА ---
users_db = []
videos_db = []
comments_db = []
likes_db = []  # user_id + video_id
subscriptions_db = []  # subscriber_id + channel_id
user_counter = 1
comment_counter = 1

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def get_user_by_email(email: str):
    for u in users_db:
        if u["email"] == email:
            return u
    return None

def get_user_by_username(username: str):
    for u in users_db:
        if u["username"] == username:
            return u
    return None

def get_user_by_id(user_id: int):
    for u in users_db:
        if u["id"] == user_id:
            return u
    return None

def has_liked(user_id: int, video_id: str):
    for like in likes_db:
        if like["user_id"] == user_id and like["video_id"] == video_id:
            return True
    return False

def is_subscribed(subscriber_id: int, channel_id: int):
    for sub in subscriptions_db:
        if sub["subscriber_id"] == subscriber_id and sub["channel_id"] == channel_id:
            return True
    return False

# --- ПОЛЬЗОВАТЕЛИ ---
@app.get("/")
def root():
    return {"message": "Let's FioHub API"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/register")
def register(user: UserRegister):
    if get_user_by_email(user.email):
        raise HTTPException(400, "Email already exists")
    if get_user_by_username(user.username):
        raise HTTPException(400, "Username already exists")
    
    global user_counter
    new_user = {
        "id": user_counter,
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "channel_name": f"{user.username}'s Channel",
        "subscribers_count": 0
    }
    users_db.append(new_user)
    user_counter += 1
    
    return {
        "id": new_user["id"],
        "username": new_user["username"],
        "email": new_user["email"],
        "channel_name": new_user["channel_name"]
    }

@app.post("/api/login")
def login(user: UserLogin):
    db_user = get_user_by_email(user.email)
    if not db_user or db_user["password"] != user.password:
        raise HTTPException(401, "Invalid email or password")
    
    token = create_token(db_user["id"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": db_user["id"],
            "username": db_user["username"],
            "email": db_user["email"],
            "channel_name": db_user["channel_name"]
        }
    }

@app.get("/api/me")
def get_me(token: str = Depends(oauth2_scheme)):
    user_id = decode_token(token)
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "channel_name": user["channel_name"],
        "subscribers_count": user.get("subscribers_count", 0)
    }

@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return {
        "id": user["id"],
        "username": user["username"],
        "channel_name": user["channel_name"],
        "subscribers_count": user.get("subscribers_count", 0)
    }

# --- ПОДПИСКИ ---
@app.post("/api/subscribe/{channel_id}")
def subscribe(channel_id: int, token: str = Depends(oauth2_scheme)):
    subscriber_id = decode_token(token)
    if subscriber_id == channel_id:
        raise HTTPException(400, "Cannot subscribe to yourself")
    
    if is_subscribed(subscriber_id, channel_id):
        raise HTTPException(400, "Already subscribed")
    
    subscriptions_db.append({
        "subscriber_id": subscriber_id,
        "channel_id": channel_id,
        "created_at": datetime.now().isoformat()
    })
    
    # Увеличиваем счётчик подписчиков у канала
    for user in users_db:
        if user["id"] == channel_id:
            user["subscribers_count"] = user.get("subscribers_count", 0) + 1
            break
    
    return {"message": "Subscribed"}

@app.delete("/api/subscribe/{channel_id}")
def unsubscribe(channel_id: int, token: str = Depends(oauth2_scheme)):
    subscriber_id = decode_token(token)
    global subscriptions_db
    subscriptions_db = [s for s in subscriptions_db if not (s["subscriber_id"] == subscriber_id and s["channel_id"] == channel_id)]
    
    for user in users_db:
        if user["id"] == channel_id:
            user["subscribers_count"] = max(0, user.get("subscribers_count", 0) - 1)
            break
    
    return {"message": "Unsubscribed"}

@app.get("/api/subscribers/{channel_id}")
def get_subscribers_count(channel_id: int):
    count = sum(1 for s in subscriptions_db if s["channel_id"] == channel_id)
    return {"count": count}

@app.get("/api/is_subscribed/{channel_id}")
def check_subscribed(channel_id: int, token: str = Depends(oauth2_scheme)):
    subscriber_id = decode_token(token)
    return {"subscribed": is_subscribed(subscriber_id, channel_id)}

# --- ВИДЕО ---
@app.get("/api/videos")
def get_all_videos():
    return {"videos": videos_db, "total": len(videos_db)}

@app.post("/api/videos/upload")
async def upload_video(
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme)
):
    user_id = decode_token(token)
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(401, "Unauthorized")
    
    video_id = str(uuid.uuid4())[:8]
    file_path = f"{UPLOAD_DIR}/{video_id}.mp4"
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    new_video = {
        "id": video_id,
        "title": title,
        "description": description,
        "views": 0,
        "likes": 0,
        "uploader_id": user["id"],
        "uploader_name": user["username"],
        "created_at": datetime.now().isoformat(),
        "file_path": file_path
    }
    videos_db.append(new_video)
    
    return {"message": "Uploaded", "video_id": video_id, "file_size": len(content)}

@app.get("/api/videos/{video_id}")
def get_video(video_id: str):
    for v in videos_db:
        if v["id"] == video_id:
            v["views"] += 1
            return v
    raise HTTPException(404, "Video not found")

@app.get("/api/videos/{video_id}/stream")
def stream_video(video_id: str):
    for v in videos_db:
        if v["id"] == video_id:
            file_path = v.get("file_path", f"{UPLOAD_DIR}/{video_id}.mp4")
            if os.path.exists(file_path):
                return FileResponse(file_path, media_type="video/mp4", headers={"Accept-Ranges": "bytes"})
    raise HTTPException(404, "File not found")

# --- ЛАЙКИ (только один раз) ---
@app.post("/api/videos/{video_id}/like")
def like_video(video_id: str, token: str = Depends(oauth2_scheme)):
    user_id = decode_token(token)
    
    # Проверяем, не лайкал ли уже
    if has_liked(user_id, video_id):
        raise HTTPException(400, "You already liked this video")
    
    # Находим видео
    for v in videos_db:
        if v["id"] == video_id:
            v["likes"] += 1
            likes_db.append({
                "user_id": user_id,
                "video_id": video_id,
                "created_at": datetime.now().isoformat()
            })
            return {"likes": v["likes"], "message": "Liked"}
    
    raise HTTPException(404, "Video not found")

@app.get("/api/videos/{video_id}/has_liked")
def check_liked(video_id: str, token: str = Depends(oauth2_scheme)):
    user_id = decode_token(token)
    return {"liked": has_liked(user_id, video_id)}

# --- КОММЕНТАРИИ ---
@app.post("/api/videos/{video_id}/comments")
def add_comment(
    video_id: str,
    comment: CommentCreate,
    token: str = Depends(oauth2_scheme)
):
    user_id = decode_token(token)
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(401, "Unauthorized")
    
    global comment_counter
    new_comment = {
        "id": comment_counter,
        "video_id": video_id,
        "text": comment.text,
        "author_id": user_id,
        "author_name": user["username"],
        "likes": 0,
        "created_at": datetime.now().isoformat()
    }
    comments_db.append(new_comment)
    comment_counter += 1
    
    return new_comment

@app.get("/api/videos/{video_id}/comments")
def get_comments(video_id: str):
    video_comments = [c for c in comments_db if c["video_id"] == video_id]
    video_comments.sort(key=lambda x: x["created_at"], reverse=True)
    return video_comments

@app.post("/api/comments/{comment_id}/like")
def like_comment(comment_id: int, token: str = Depends(oauth2_scheme)):
    user_id = decode_token(token)
    
    for c in comments_db:
        if c["id"] == comment_id:
            c["likes"] += 1
            return {"likes": c["likes"]}
    
    raise HTTPException(404, "Comment not found")

@app.delete("/api/comments/{comment_id}")
def delete_comment(comment_id: int, token: str = Depends(oauth2_scheme)):
    user_id = decode_token(token)
    global comments_db
    
    for i, c in enumerate(comments_db):
        if c["id"] == comment_id:
            if c["author_id"] != user_id:
                raise HTTPException(403, "You can only delete your own comments")
            comments_db.pop(i)
            return {"message": "Comment deleted"}
    
    raise HTTPException(404, "Comment not found")

@app.get("/api/channel/{username}")
def get_channel(username: str):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(404, "Channel not found")
    
    user_videos = [v for v in videos_db if v["uploader_name"] == user["username"]]
    return {
        "channel_name": user["channel_name"],
        "username": user["username"],
        "subscribers_count": user.get("subscribers_count", 0),
        "videos": user_videos
    }

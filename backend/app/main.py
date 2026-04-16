from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid
import os

# --- Конфигурация ---
SECRET_KEY = "your-super-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

os.makedirs("uploads", exist_ok=True)

app = FastAPI(title="Let's FioHub API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Безопасность ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("sub"))
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- Модели ---
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    channel_name: str

class VideoOut(BaseModel):
    id: str
    title: str
    description: str
    views: int
    likes: int
    uploader_name: str
    created_at: str

# --- Хранилища (в памяти) ---
users_db = []
videos_db = []
user_counter = 1

# --- Вспомогательные функции ---
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

# --- API ---
@app.get("/")
def root():
    return {"message": "Let's FioHub API"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Регистрация
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
        "password_hash": hash_password(user.password),
        "channel_name": f"{user.username}'s Channel"
    }
    users_db.append(new_user)
    user_counter += 1
    
    return {
        "id": new_user["id"],
        "username": new_user["username"],
        "email": new_user["email"],
        "channel_name": new_user["channel_name"]
    }

# Вход
@app.post("/api/login")
def login(user: UserLogin):
    db_user = get_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
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

# Получить текущего пользователя
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
        "channel_name": user["channel_name"]
    }

# Получить канал пользователя
@app.get("/api/channel/{username}")
def get_channel(username: str):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(404, "Channel not found")
    
    user_videos = [v for v in videos_db if v["uploader_name"] == user["username"]]
    return {
        "channel_name": user["channel_name"],
        "username": user["username"],
        "videos": user_videos
    }

# Все видео
@app.get("/api/videos")
def get_all_videos():
    return {"videos": videos_db, "total": len(videos_db)}

# Загрузка видео
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
    file_path = f"uploads/{video_id}.mp4"
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    new_video = {
        "id": video_id,
        "title": title,
        "description": description,
        "views": 0,
        "likes": 0,
        "uploader_name": user["username"],
        "created_at": datetime.now().isoformat()
    }
    videos_db.append(new_video)
    
    return {"message": "Uploaded", "video_id": video_id}

# Получить видео по ID
@app.get("/api/videos/{video_id}")
def get_video(video_id: str):
    for v in videos_db:
        if v["id"] == video_id:
            v["views"] += 1
            return v
    raise HTTPException(404, "Video not found")

# Потоковое воспроизведение
@app.get("/api/videos/{video_id}/stream")
def stream_video(video_id: str):
    file_path = f"uploads/{video_id}.mp4"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4")
    raise HTTPException(404, "File not found")

# Лайк
@app.post("/api/videos/{video_id}/like")
def like_video(video_id: str):
    for v in videos_db:
        if v["id"] == video_id:
            v["likes"] += 1
            return {"likes": v["likes"]}
    raise HTTPException(404, "Video not found")

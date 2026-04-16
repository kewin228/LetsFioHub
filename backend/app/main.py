from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os

# --- Конфигурация ---
SECRET_KEY = "your-super-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

os.makedirs("uploads", exist_ok=True)

app = FastAPI(title="Let's FioHub API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Хэширование паролей и JWT ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Pydantic модели ---
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    channel_name: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Хранилища ---
users_db = []
videos_db = []
user_counter = 1

def get_user_by_email(email: str):
    for user in users_db:
        if user["email"] == email:
            return user
    return None

def get_user_by_username(username: str):
    for user in users_db:
        if user["username"] == username:
            return user
    return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    for user in users_db:
        if user["id"] == user_id:
            return user
    raise credentials_exception

# --- API ---
@app.get("/")
def root():
    return {"message": "Let's FioHub API v2.0", "endpoints": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/api/register", response_model=UserOut)
async def register(user_data: UserCreate):
    if get_user_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if get_user_by_username(user_data.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    global user_counter
    hashed_password = get_password_hash(user_data.password)
    new_user = {
        "id": user_counter,
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "channel_name": f"{user_data.username}'s Channel"
    }
    users_db.append(new_user)
    user_counter += 1
    return {"id": new_user["id"], "username": new_user["username"], "email": new_user["email"], "channel_name": new_user["channel_name"]}

@app.post("/api/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user["id"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=UserOut)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"id": current_user["id"], "username": current_user["username"], "email": current_user["email"], "channel_name": current_user["channel_name"]}

@app.get("/api/channels/{username}")
async def get_channel(username: str):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Channel not found")
    user_videos = [v for v in videos_db if v["uploader_id"] == user["id"]]
    return {
        "channel_name": user["channel_name"],
        "username": user["username"],
        "videos": user_videos
    }

@app.post("/api/v1/videos/upload")
async def upload_video(
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    video_id = str(uuid.uuid4())[:8]
    file_path = f"uploads/{video_id}.mp4"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    new_video = {
        "id": video_id,
        "title": title,
        "description": description,
        "file_path": file_path,
        "uploader_id": current_user["id"],
        "uploader_name": current_user["username"],
        "views": 0,
        "likes": 0,
        "created_at": datetime.utcnow().isoformat()
    }
    videos_db.append(new_video)
    return {"message": "Video uploaded", "video_id": video_id}

@app.delete("/api/v1/videos/{video_id}")
async def delete_video(video_id: str, current_user: dict = Depends(get_current_user)):
    global videos_db
    for i, video in enumerate(videos_db):
        if video["id"] == video_id:
            if video["uploader_id"] != current_user["id"]:
                raise HTTPException(status_code=403, detail="You can only delete your own videos")
            if os.path.exists(video["file_path"]):
                os.remove(video["file_path"])
            videos_db.pop(i)
            return {"message": "Video deleted"}
    raise HTTPException(status_code=404, detail="Video not found")

@app.get("/api/v1/videos")
async def get_all_videos():
    result = []
    for video in videos_db:
        result.append({
            "id": video["id"],
            "title": video["title"],
            "description": video["description"],
            "views": video["views"],
            "likes": video["likes"],
            "uploader_name": video["uploader_name"],
            "created_at": video["created_at"]
        })
    return {"videos": result, "total": len(result)}

@app.get("/api/v1/videos/{video_id}")
async def get_video(video_id: str):
    for video in videos_db:
        if video["id"] == video_id:
            video["views"] += 1
            return video
    raise HTTPException(status_code=404, detail="Video not found")

@app.get("/api/v1/videos/{video_id}/stream")
async def stream_video(video_id: str):
    for video in videos_db:
        if video["id"] == video_id:
            file_path = video["file_path"]
            if os.path.exists(file_path):
                return FileResponse(file_path, media_type="video/mp4")
    raise HTTPException(status_code=404, detail="Video file not found")

@app.post("/api/v1/videos/{video_id}/like")
async def like_video(video_id: str, user_id: int = 1):
    for video in videos_db:
        if video["id"] == video_id:
            video["likes"] += 1
            return {"message": "Liked", "likes": video["likes"]}
    raise HTTPException(status_code=404, detail="Video not found")

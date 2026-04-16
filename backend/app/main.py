from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid
import os

SECRET_KEY = "your-secret-key-change-it"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

os.makedirs("uploads", exist_ok=True)

app = FastAPI(title="Let's FioHub API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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

users_db = []
videos_db = []
user_counter = 1

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

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        for u in users_db:
            if u["id"] == user_id:
                return u
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/register", response_model=UserOut)
async def register(user: UserCreate):
    if get_user_by_email(user.email):
        raise HTTPException(400, "Email already registered")
    if get_user_by_username(user.username):
        raise HTTPException(400, "Username taken")
    global user_counter
    new_user = {
        "id": user_counter,
        "username": user.username,
        "email": user.email,
        "hashed_password": get_password_hash(user.password),
        "channel_name": f"{user.username}'s Channel"
    }
    users_db.append(new_user)
    user_counter += 1
    return new_user

@app.post("/api/token", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form.username)
    if not user or not verify_password(form.password, user["hashed_password"]):
        raise HTTPException(400, "Invalid credentials")
    return {"access_token": create_access_token({"sub": user["id"]}), "token_type": "bearer"}

@app.get("/api/users/me", response_model=UserOut)
async def me(current_user = Depends(get_current_user)):
    return current_user

@app.get("/api/v1/videos")
async def get_videos():
    return {"videos": videos_db, "total": len(videos_db)}

@app.post("/api/v1/videos/upload")
async def upload_video(
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    video_id = str(uuid.uuid4())[:8]
    file_path = f"uploads/{video_id}.mp4"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    videos_db.append({
        "id": video_id, "title": title, "description": description,
        "file_path": file_path, "uploader_name": current_user["username"],
        "views": 0, "likes": 0, "created_at": datetime.now().isoformat()
    })
    return {"message": "Uploaded", "video_id": video_id}

@app.get("/api/v1/videos/{video_id}")
async def get_video(video_id: str):
    for v in videos_db:
        if v["id"] == video_id:
            v["views"] += 1
            return v
    raise HTTPException(404, "Not found")

@app.get("/api/v1/videos/{video_id}/stream")
async def stream(video_id: str):
    for v in videos_db:
        if v["id"] == video_id and os.path.exists(v["file_path"]):
            return FileResponse(v["file_path"], media_type="video/mp4")
    raise HTTPException(404, "Not found")

@app.get("/health")
async def health():
    return {"status": "ok"}

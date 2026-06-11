from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
from datetime import datetime

app = FastAPI(title="Let'sFioHub API", version="Let's-1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("media", exist_ok=True)

# Инициализация SQLite базы
def init_db():
    conn = sqlite3.connect('letsfiohub.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            channel_name TEXT UNIQUE,
            is_verified BOOLEAN DEFAULT 0,
            total_subscribers INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            file_path TEXT,
            thumbnail_url TEXT,
            duration INTEGER DEFAULT 0,
            views_count INTEGER DEFAULT 0,
            likes_count INTEGER DEFAULT 0,
            is_public BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gamer_styles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            theme_name TEXT,
            primary_color TEXT,
            secondary_color TEXT,
            background_dark TEXT
        )
    ''')
    
    # Добавляем геймерские стили
    cursor.execute('SELECT COUNT(*) FROM gamer_styles')
    if cursor.fetchone()[0] == 0:
        styles = [
            ('Cyberpunk Neon', 'cyberpunk', '#00FFFF', '#FF00FF', '#0A0A0F'),
            ('Call of Duty', 'cod', '#FF6B00', '#FFD700', '#1C1C1C'),
            ('Fortnite', 'fortnite', '#9D4EDD', '#00F5FF', '#2D1B4E'),
            ('Minecraft', 'minecraft', '#5D8C3A', '#8B7355', '#1E1E1E'),
            ('Valorant', 'valorant', '#FF4655', '#FFFFFF', '#0F1923'),
            ('League of Legends', 'lol', '#C8AA6E', '#0AC8B9', '#091428'),
            ('Dark Souls', 'darksouls', '#8B0000', '#FFD700', '#0D0D0D'),
            ('Apex Legends', 'apex', '#F26522', '#FFFFFF', '#1A1A1A'),
            ('Default', 'default', '#FF0000', '#CC0000', '#0F0F0F')
        ]
        cursor.executemany('INSERT INTO gamer_styles (name, theme_name, primary_color, secondary_color, background_dark) VALUES (?, ?, ?, ?, ?)', styles)
    
    conn.commit()
    conn.close()

# Инициализируем БД при старте
init_db()

@app.get("/")
async def root():
    return {
        "message": "🎬 Welcome to Let'sFioHub API",
        "version": "Let's-1.0",
        "database": "SQLite",
        "status": "running"
    }

@app.get("/api/v1/video")
async def get_videos():
    conn = sqlite3.connect('letsfiohub.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM videos ORDER BY created_at DESC LIMIT 20')
    videos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return videos if videos else [{
        "id": 1,
        "title": "Добро пожаловать в Let'sFioHub!",
        "description": "Это первый видеохостинг с геймерскими темами",
        "views_count": 1,
        "likes_count": 1,
        "duration": 0
    }]

@app.get("/api/v1/gamer-styles")
async def get_gamer_styles():
    conn = sqlite3.connect('letsfiohub.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM gamer_styles')
    styles = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return styles

@app.post("/api/v1/video/upload")
async def upload_video(title: str, description: str = "", user_id: int = 1):
    conn = sqlite3.connect('letsfiohub.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO videos (title, description, user_id) VALUES (?, ?, ?)',
        (title, description, user_id)
    )
    video_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": video_id, "title": title, "status": "uploaded"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Let'sFioHub", "database": "SQLite"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

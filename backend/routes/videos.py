from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Video
from schemas import VideoCreate, VideoResponse

router = APIRouter(prefix="/api/videos", tags=["videos"])

@router.get("/", response_model=List[VideoResponse])
def get_videos(style: str = None, db: Session = Depends(get_db)):
    query = db.query(Video)
    if style:
        query = query.filter(Video.style == style)
    return query.order_by(Video.created_at.desc()).all()

@router.post("/", response_model=VideoResponse)
def create_video(video: VideoCreate, db: Session = Depends(get_db)):
    db_video = Video(**video.dict())
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

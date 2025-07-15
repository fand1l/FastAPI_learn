import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from models.models import Track, User
from routes.dependencies import get_current_user_from_cookie, get_db
from schemas.schemas import TrackCreate, TrackOut
from fastapi.responses import FileResponse

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/tracks", tags=["Tracks"])


@router.get("/", response_model=list[TrackOut])
def get_all_tracks(db: Session = Depends(get_db)):
    return db.query(Track).all()


@router.post("/add", response_model=TrackOut)
async def upload_track(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    track = TrackCreate(name=file.filename)
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())
    db_track = Track(
        title=file.filename,
        filename=file.filename,
        author_id=current_user.id,
    )
    db.add(db_track)
    db.commit()
    db.refresh(db_track)
    return db_track


@router.put("/update/{id}", response_model=TrackOut)
def update_track(
    id: int,
    title: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    track = db.query(Track).filter(Track.id == id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Трек не знайдено")
    if track.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостатньо прав")
    track.title = title
    db.commit()
    db.refresh(track)
    return track


@router.post("/delete/{id}")
def delete_track(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    track = db.query(Track).filter(Track.id == id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Трек не знайдено")
    if track.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостатньо прав")
    db.delete(track)
    db.commit()
    filepath = os.path.join(UPLOAD_DIR, track.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return {"message": "Трек видалено"}


@router.get("/play/{id}")
def play_track(id: int, db: Session = Depends(get_db)):
    track = db.query(Track).filter(Track.id == id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Трек не знайдено")
    filepath = os.path.join(UPLOAD_DIR, track.filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Файл не знайдено")
    return FileResponse(filepath, media_type="audio/mpeg")

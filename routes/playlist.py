from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from models.models import Playlist, Track, User
from routes.dependencies import get_current_user, get_db
from schemas.schemas import PlaylistOut, TrackOut

router = APIRouter(prefix="/playlists", tags=["Playlists"])


@router.post("/add", response_model=PlaylistOut)
def create_playlist(
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    playlist = Playlist(name=name, user_id=current_user.id)
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist


@router.put("/update/{id}", response_model=PlaylistOut)
def update_playlist(
    id: int,
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    playlist = db.query(Playlist).filter(Playlist.id == id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    playlist.name = name
    db.commit()
    db.refresh(playlist)
    return playlist


@router.delete("/delete/{id}")
def delete_playlist(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    playlist = db.query(Playlist).filter(Playlist.id == id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db.delete(playlist)
    db.commit()
    return {"message": "Playlist deleted"}


@router.get("/", response_model=list[PlaylistOut])
def get_user_playlists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Playlist).filter(Playlist.user_id == current_user.id).all()


@router.get("/{id}", response_model=PlaylistOut)
def get_playlist(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    playlist = db.query(Playlist).filter(Playlist.id == id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return playlist


@router.get("/{id}/tracks", response_model=list[TrackOut])
def list_playlist_tracks(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    playlist = db.query(Playlist).filter(Playlist.id == id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return playlist.tracks


@router.post("/{id}/tracks/{track_id}", response_model=PlaylistOut)
def add_track_to_playlist(
    id: int,
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    playlist = db.query(Playlist).filter(Playlist.id == id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    if track not in playlist.tracks:
        playlist.tracks.append(track)
        db.commit()
    db.refresh(playlist)
    return playlist


@router.delete("/{id}/tracks/{track_id}")
def remove_track_from_playlist(
    id: int,
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    playlist = db.query(Playlist).filter(Playlist.id == id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track or track not in playlist.tracks:
        raise HTTPException(status_code=404, detail="Track not found")
    playlist.tracks.remove(track)
    db.commit()
    return {"message": "Track removed"}
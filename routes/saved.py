from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from routes.auth import get_db
from db_models.social import Saved, Like, Post
from baseModels.saved import SavedCreate, SavedResponse

router = APIRouter(tags=["Saved"])

# Save a post
@router.post("/save", response_model=SavedResponse)
def save_post(data: SavedCreate, db: Session = Depends(get_db)):
    # Check if already saved
    existing = db.query(Saved).filter_by(user_id=data.user_id, post_id=data.post_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Post already saved")

    saved_post = Saved(user_id=data.user_id, post_id=data.post_id)
    db.add(saved_post)
    db.commit()
    db.refresh(saved_post)
    return saved_post

# Unsave a post
@router.delete("/unsave/{user_id}/{post_id}")
def unsave_post(user_id: int, post_id: int, db: Session = Depends(get_db)):
    saved_post = db.query(Saved).filter_by(user_id=user_id, post_id=post_id).first()
    if not saved_post:
        raise HTTPException(status_code=404, detail="Saved post not found")

    db.delete(saved_post)
    db.commit()
    return {"message": "Post unsaved successfully"}

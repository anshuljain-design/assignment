from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from routes.auth import get_db
from db_models.social import Like
from db_models.user import User
from baseModels.like_models import CreateLike

router = APIRouter(tags=["Likes"])


# --------------------------
# Create a like
# --------------------------
@router.post("/")
def create_like(like: CreateLike, db: Session = Depends(get_db)):
    exists = db.query(Like).filter(
        Like.user_id == like.user_id,
        Like.post_id == like.post_id
    ).first()

    if exists:
        return exists

    new_like = Like(
        user_id=like.user_id,
        post_id=like.post_id
    )
    db.add(new_like)
    db.commit()
    db.refresh(new_like)
    return new_like


# --------------------------
# Delete a like
# --------------------------
@router.post("/delete")
def delete_like(like: CreateLike, db: Session = Depends(get_db)):
    res = db.query(Like).filter(
        Like.post_id == like.post_id,
        Like.user_id == like.user_id
    ).first()
    if not res:
        raise HTTPException(
            detail=f"Like not found"
        )
    
    db.delete(res)
    db.commit()
    return {"message": "Like deleted successfully"}


# --------------------------
# Get all likes for a post including user name
# --------------------------
@router.get("/{post_id}")
def get_liked(post_id: int, db: Session = Depends(get_db)):
    likes = db.query(Like).join(User, Like.user_id == User.id).all()
    
    # Prepare response with user names
    response = []
    for like in likes:
        if like.post_id != post_id:
            continue
        response.append({
            "like_id": like.id,
            "user_id": like.user_id,
            "user_name": like.user.name,  # fetch user name
            "post_id": like.post_id,
            "created_at": like.created_at
        })

    return response

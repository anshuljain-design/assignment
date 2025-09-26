from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List
from routes.auth import get_db
from db_models.social import Post
from db_models.user import User
from baseModels.post_models import PostCreate, PostUpdate, PostOut
from db_models.social import Post, Like, Comment
from db_models.social import Saved


router = APIRouter(

    tags=["Profile"]
)


@router.get("/{id}/{user_id}")
def get_profile(id: int, user_id: int, db: Session = Depends(get_db)):
    # -------------------
    # Fetch the profile user info
    # -------------------
    profile_user = db.query(User).filter(User.id == id).first()
    if not profile_user:
        raise HTTPException(status_code=404, detail="User not found")

    # -------------------
    # 1️⃣ Profile user's own posts
    # -------------------
    user_posts = db.query(Post).filter(Post.user_id == id).order_by(Post.created_at.desc()).all()
    posts_list = []
    for post in user_posts:
        like_count = db.query(func.count(Like.id)).filter(Like.post_id == post.id).scalar()
        comment_count = db.query(func.count(Comment.id)).filter(Comment.post_id == post.id).scalar()
        is_liked = db.query(Like).filter(Like.post_id == post.id, Like.user_id == user_id).first() is not None
        is_saved = db.query(Saved).filter(Saved.post_id == post.id, Saved.user_id == user_id).first() is not None

        posts_list.append({
            "id": post.id,
            "caption": post.caption,
            "image_url": post.image_url,
            "created_at": post.created_at,
            "like_count": like_count,
            "comment_count": comment_count,
            "is_liked_by_you": is_liked,
            "is_saved_by_you": is_saved,
            "creator_user_id": post.user_id,
            "creator_name": post.user.name
        })

    # -------------------
    # 2️⃣ Profile user's saved posts
    # -------------------
    saved_entries = (
        db.query(Saved)
        .options(joinedload(Saved.post))
        .filter(Saved.user_id == id)
        .all()
    )

    saved_list = []
    for saved in saved_entries:
        post = saved.post
        if not post:
            continue

        like_count = db.query(func.count(Like.id)).filter(Like.post_id == post.id).scalar()
        comment_count = db.query(func.count(Comment.id)).filter(Comment.post_id == post.id).scalar()
        is_liked = db.query(Like).filter(Like.post_id == post.id, Like.user_id == user_id).first() is not None
        is_saved = db.query(Saved).filter(Saved.post_id == post.id, Saved.user_id == user_id).first() is not None

        saved_list.append({
            "id": post.id,
            "caption": post.caption,
            "image_url": post.image_url,
            "created_at": post.created_at,
            "like_count": like_count,
            "comment_count": comment_count,
            "is_liked_by_you": is_liked,
            "is_saved_by_you": is_saved,
            "creator_user_id": post.user_id,
            "creator_name": post.user.name
        })

    return {
        "user_id": profile_user.id,
        "name": profile_user.name,
        "email": profile_user.email,  # ✅ Added email
        "posts": posts_list,
        "saved_posts": saved_list
    }

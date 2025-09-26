from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from routes.auth import get_db
from db_models.social import Post, Like, Comment, Saved
from baseModels.post_models import PostCreate

router = APIRouter(
    tags=["Posts"]
)

# ✅ Create a new post
@router.post("/")
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    new_post = Post(
        caption=post.caption,
        image_url=post.image_url,
        user_id=post.user_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# ✅ Get paginated posts with likes, comments, and saved status
@router.get("/")
def get_posts(
    page: int = Query(1, ge=1),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    page_size = 5
    offset = (page - 1) * page_size

    if not user_id:
        raise HTTPException(status_code=401, detail="Please login to view posts")

    posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .all()
    )

    response = []
    for post in posts:
        like_count = db.query(func.count(Like.id)).filter(Like.post_id == post.id).scalar()
        comment_count = db.query(func.count(Comment.id)).filter(Comment.post_id == post.id).scalar()
        top_comments = (
            db.query(Comment)
            .filter(Comment.post_id == post.id)
            .order_by(Comment.created_at.desc())
            .limit(2)
            .all()
        )

        is_liked = (
            db.query(Like)
            .filter(Like.post_id == post.id, Like.user_id == user_id)
            .first()
            is not None
        )

        is_saved = (
            db.query(Saved)
            .filter(Saved.post_id == post.id, Saved.user_id == user_id)
            .first()
            is not None
        )

        response.append({
            "id": post.id,
            "caption": post.caption,
            "image_url": post.image_url,
            "created_at": post.created_at,
            "user_id": post.user_id,
            "user_name": post.user.name,
            "like_count": like_count,
            "comment_count": comment_count,
            "is_liked_by_you": is_liked,
            "is_saved_by_you": is_saved,
            "top_comments": [
                {
                    "id": c.id,
                    "user_id": c.user_id,
                    "comment_text": c.comment_text,
                    "created_at": c.created_at
                }
                for c in top_comments
            ]
        })

    return {
        "page": page,
        "page_size": page_size,
        "posts": response
    }


# ✅ Delete a post
@router.delete("/")
def delete_post(
    post_id: int = Query(...),
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found or not owned by user")

    # Delete related likes, comments, saved first (optional, depending on cascade rules)
    db.query(Like).filter(Like.post_id == post_id).delete()
    db.query(Comment).filter(Comment.post_id == post_id).delete()
    db.query(Saved).filter(Saved.post_id == post_id).delete()

    db.delete(post)
    db.commit()

    return {"detail": "Post deleted successfully"}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from routes.auth import get_db
from db_models.social import Comment
from db_models.user import User
from baseModels.comment_models import CommentCreate

router = APIRouter(tags=["Comments"])


# --------------------------
# Create a new comment
# --------------------------
@router.post("/")
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    new_comment = Comment(
        comment_text=comment.comment,
        user_id=comment.commentor_id,
        post_id=comment.post_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


# --------------------------
# Fetch all comments for a post including commenter name
# --------------------------
@router.get("/{post_id}")
def fetch_comment(post_id: int, db: Session = Depends(get_db)):
    comments = (
        db.query(Comment)
        .join(User, Comment.user_id == User.id)
        .filter(Comment.post_id == post_id)
        .all()
    )
    if not comments:
        raise HTTPException(status_code=404, detail="No comments found")

    response = []
    for c in comments:
        response.append({
            "comment_id": c.id,
            "post_id": c.post_id,
            "comment_text": c.comment_text,
            "commentor_id": c.user_id,
            "commentor_name": c.user.name,  # ✅ commenter name
            "created_at": c.created_at
        })

    return response


# --------------------------
# Delete a comment
# --------------------------
@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully"}

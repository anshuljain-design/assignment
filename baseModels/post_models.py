from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from baseModels.auth_model import LoginModel

class CommentOut(BaseModel):
    id: int
    comment_text: str
    created_at: datetime
    user_id: int
    post_id: int

    class Config:
        orm_mode = True  # ✅ important


class LikesOut(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        orm_mode = True  # ✅ important


class UserOut(BaseModel):
    id: int
    email: str
    username: str

    class Config:
        orm_mode = True



class PostCreate(BaseModel):
    caption: str
    image_url: Optional[str] = None
    user_id: int


class PostUpdate(BaseModel):
    caption: Optional[str] = None
    image_url: Optional[str] = None


class PostOut(BaseModel):
    id: int
    caption: str
    image_url: Optional[str]
    created_at: datetime
    user_id: UserOut
    comments: List[CommentOut] = []
    likes: List[LikesOut] = []

    class Config:
        orm_mode = True

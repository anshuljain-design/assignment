from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CommentCreate(BaseModel):
    comment : str
    commentor_id : int
    post_id : int


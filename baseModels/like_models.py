from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreateLike(BaseModel):
    user_id : int
    post_id : int

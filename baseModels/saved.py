from pydantic import BaseModel
from datetime import datetime

# Base schema (common fields)
class SavedBase(BaseModel):
    post_id: int
    user_id:int

# Schema for creating a saved record
class SavedCreate(SavedBase):
    pass

# Schema for returning saved record
class SavedResponse(SavedBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

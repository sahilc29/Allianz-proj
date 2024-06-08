from pydantic import BaseModel
from datetime import datetime


class CommentModel(BaseModel):
    id: int
    username: str
    text: str
    created_at: datetime
    subfeddit_id: int

    class Config:
        from_attributes = True

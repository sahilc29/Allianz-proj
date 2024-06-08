from pydantic import BaseModel


class CommentResponse(BaseModel):
    id: int
    text: str
    polarity: float
    classification: str

    class Config:
        from_attributes = True

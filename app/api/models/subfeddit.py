from pydantic import BaseModel


class SubfedditModel(BaseModel):
    id: int
    username: str
    title: str
    description: str

    class Config:
        from_attributes = True

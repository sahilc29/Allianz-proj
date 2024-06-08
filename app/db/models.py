from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.db import Base
from sqlalchemy.orm import relationship


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    text = Column(Text)
    created_at = Column(DateTime)
    subfeddit_id = Column(Integer, ForeignKey('subfeddits.id'))

    subfeddit = relationship("Subfeddit", back_populates="comments")


class Subfeddit(Base):
    __tablename__ = "subfeddits"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    title = Column(String)
    description = Column(String)
    comments = relationship("Comment", back_populates="subfeddit")

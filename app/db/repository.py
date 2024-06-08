from sqlalchemy.orm import Session
from app.db.models import Comment, Subfeddit
from sqlalchemy import desc, distinct


def get_subfeddits(db: Session):
    return db.query(distinct(Subfeddit.title)).all()


def get_recent_comments(db: Session, subfeddit_id: int, limit: int = 25):
    return db.query(Comment).filter(Comment.subfeddit_id == subfeddit_id).order_by(desc(Comment.created_at)).limit(limit).all()
